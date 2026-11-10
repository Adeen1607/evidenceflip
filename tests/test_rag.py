"""Reproducible local RAG and retrieval evaluation tests. No hosted model needed."""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evidenceflip.rag import (BM25Retriever, Chunk, OllamaGenerator, RAGPipeline,
                              Source, chunk_sources, evaluate_retrieval, load_sources)
from evidenceflip.rag_cli import main

ROOT = Path(__file__).resolve().parents[1]


class RAGPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_sources(ROOT)
        cls.index = BM25Retriever(chunk_sources(cls.sources))

    def test_corpus_has_verifiable_sources(self):
        self.assertEqual(len(self.sources), 11)
        self.assertEqual(len({source.id for source in self.sources}), len(self.sources))
        self.assertTrue(all(len(s.sha256) == 64 for s in self.sources))

    def test_checksum_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "sources").mkdir()
            (base / "sources" / "x.md").write_text("A correct document", encoding="utf-8")
            good = hashlib.sha256(b"A correct document").hexdigest()
            manifest = {"sources": [{"id": "x", "path": "sources/x.md", "sha256": good}]}
            (base / "sources" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(load_sources(base)[0].text, "A correct document")
            (base / "sources" / "x.md").write_text("An altered document", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "integrity mismatch"):
                load_sources(base)

    def test_registry_path_escape_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "sources").mkdir()
            (base / "sources" / "manifest.json").write_text(json.dumps(
                {"sources": [{"id": "x", "path": "../outside.md", "sha256": "0" * 64}]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside root"):
                load_sources(base)

    def test_duplicate_source_id_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "sources").mkdir()
            (base / "sources" / "x.md").write_text("Source", encoding="utf-8")
            entry = {"id": "x", "path": "sources/x.md", "sha256": hashlib.sha256(b"Source").hexdigest()}
            (base / "sources" / "manifest.json").write_text(json.dumps({"sources": [entry, entry]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate source ID"):
                load_sources(base)

    def test_chunk_overlap_and_excerpt(self):
        chunks = chunk_sources([Source("lab", "zero one two three four five six")], size=4, overlap=2)
        self.assertEqual([chunk.start_word for chunk in chunks], [0, 2, 4])
        self.assertEqual(chunks[0].text, "zero one two three")
        self.assertEqual(chunks[1].text, "two three four five")
        self.assertEqual(chunks[-1].end_word, 7)

    def test_invalid_chunking_rejected(self):
        with self.assertRaises(ValueError):
            chunk_sources(self.sources, size=3, overlap=3)

    def test_retriever_ranks_specific_source(self):
        hits = self.index.search("How many observations in Orion dataset?", top_k=3)
        self.assertEqual(hits[0].chunk.source_id, "dataset-card")
        self.assertTrue(hits[0].score > 0)

    def test_no_relevant_tokens_means_no_hit(self):
        self.assertEqual(self.index.search("qxzxvwyzzqqq"), [])

    def test_end_to_end_with_injected_generator(self):
        seen = []
        def generator(prompt):
            seen.append(prompt)
            return "Orion contains 480 synthetic observations. [dataset-card]"
        pipeline = RAGPipeline(self.index, generator)
        result = pipeline.ask("How many observations are in Orion dataset?", top_k=2)
        self.assertEqual(result.citations, ("dataset-card",))
        self.assertEqual(result.invalid_citations, ())
        self.assertEqual(result.hits[0].chunk.source_id, "dataset-card")
        self.assertIn("480 synthetic observations", seen[0])
        self.assertIn("[source:dataset-card", seen[0])
        self.assertGreaterEqual(result.elapsed_ms, 0)

    def test_fabricated_citation_is_not_silently_removed(self):
        pipeline = RAGPipeline(self.index, lambda _: "480 observations. [dataset-card] [invented]")
        result = pipeline.ask("How many observations in Orion dataset?", top_k=1)
        self.assertEqual(result.invalid_citations, ("invented",))
        self.assertEqual(result.citations, ("dataset-card", "invented"))

    def test_no_evidence_does_not_call_model(self):
        def fail(_):
            raise AssertionError("Generation must not run without retrieved evidence")
        result = RAGPipeline(self.index, fail).ask("qxzxvwyzzqqq")
        self.assertIn("Insufficient evidence", result.answer)
        self.assertFalse(result.hits)

    def test_empty_question_rejected(self):
        with self.assertRaises(ValueError):
            RAGPipeline(self.index, lambda _: "a").ask("  ")

    def test_retrieval_eval_reports_measured_stats(self):
        data = json.loads((ROOT / "examples" / "retrieval_benchmark.json").read_text(encoding="utf-8"))
        result = evaluate_retrieval(RAGPipeline(self.index, lambda _: "unused"), data["queries"], top_k=3)
        self.assertEqual(result["queries"], 11)
        self.assertGreater(result["hit_rate"], 0.5)
        self.assertGreater(result["mrr"], 0.5)

    def test_retrieval_eval_handles_unmatched_label(self):
        result = evaluate_retrieval(RAGPipeline(self.index, lambda _: "unused"),
                                    [{"question": "Orion", "relevant_sources": ["does-not-exist"]}], top_k=1)
        self.assertEqual(result["hit_rate"], 0.0)
        self.assertEqual(result["mrr"], 0.0)

    def test_ollama_adapter_contract_using_fake_http(self):
        fake = io.BytesIO(json.dumps({"message": {"content": "Observed. [dataset-card]"}}).encode("utf-8"))
        with patch("evidenceflip.rag.request.urlopen", return_value=fake) as opened:
            result = OllamaGenerator("mocked-model")("Question and passages")
        self.assertEqual(result, "Observed. [dataset-card]")
        req = opened.call_args.args[0]
        request_body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(request_body["model"], "mocked-model")
        self.assertEqual(request_body["stream"], False)
        self.assertEqual(request_body["options"]["temperature"], 0)
        self.assertEqual(req.full_url, "http://127.0.0.1:11434/api/chat")

    def test_ollama_adapter_rejects_empty(self):
        fake = io.BytesIO(json.dumps({"message": {"content": ""}}).encode("utf-8"))
        with patch("evidenceflip.rag.request.urlopen", return_value=fake):
            with self.assertRaisesRegex(RuntimeError, "empty or malformed"):
                OllamaGenerator()("Question")

    def test_bm25_no_documents_is_safe(self):
        self.assertEqual(BM25Retriever([]).search("question"), [])


if __name__ == "__main__":
    unittest.main()
