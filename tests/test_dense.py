"""Offline dense retrieval acceptance tests: no model weights or network."""
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from evidenceflip.dense import DenseRetriever, SentenceTransformerEncoder
from evidenceflip.rag import BM25Retriever, Chunk, RAGPipeline, Source, chunk_sources
from evidenceflip.rag_cli import main


class FakeEncoder:
    def __init__(self, vectors):
        self.vectors = vectors
        self.calls = []

    def encode(self, texts):
        self.calls.append(list(texts))
        return [self.vectors[text] for text in texts]


class DenseRetrieverTests(unittest.TestCase):
    def setUp(self):
        self.chunks = chunk_sources([
            Source("alpha", "The scientist examined the specimen."),
            Source("beta", "The researcher studied the sample."),
        ])
        self.vectors = {
            self.chunks[0].text: [1.0, 0.0],
            self.chunks[1].text: [0.0, 1.0],
            "investigator analyzed material": [0.0, 2.0],
        }

    def test_semantic_match_without_shared_terms_and_trace(self):
        question = "investigator analyzed material"
        self.assertEqual(BM25Retriever(self.chunks).search(question), [])
        index = DenseRetriever(self.chunks, FakeEncoder(self.vectors))
        hits = index.search(question, top_k=1)
        self.assertEqual(hits[0].chunk.source_id, "beta")
        self.assertEqual(hits[0].score, 1.0)
        answer = RAGPipeline(index, lambda _: "The researcher studied the sample. [beta]").ask(question)
        self.assertEqual(answer.citations, ("beta",))
        self.assertEqual(answer.hits[0].chunk.source_id, "beta")

    def test_source_provenance_survives_chunking_and_dense_search(self):
        source = Source("study", "A controlled laboratory note.", path="sources/study.md",
                        sha256="a" * 64, license="MIT")
        chunks = chunk_sources([source])
        encoder = FakeEncoder({chunks[0].text: [3.0, 4.0], "laboratory": [3.0, 4.0]})
        hit = DenseRetriever(chunks, encoder).search("laboratory")[0]
        self.assertEqual(hit.chunk.source_path, "sources/study.md")
        self.assertEqual(hit.chunk.source_sha256, "a" * 64)
        self.assertEqual(hit.chunk.source_license, "MIT")

    def test_stable_ties_and_empty_index(self):
        index = DenseRetriever(self.chunks, FakeEncoder({**self.vectors, "tie": [1.0, 1.0]}))
        self.assertEqual([hit.chunk.source_id for hit in index.search("tie")], ["alpha", "beta"])
        self.assertEqual(DenseRetriever([], FakeEncoder({})).search("anything"), [])
        with self.assertRaises(ValueError):
            index.search("tie", top_k=0)

    def test_rejects_bad_document_vectors(self):
        for bad in ([0.0, 0.0], [float("nan"), 1.0], [float("inf"), 0.0], [1.0], ["1", 2.0]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                DenseRetriever(self.chunks, FakeEncoder({**self.vectors, self.chunks[1].text: bad}))
        with self.assertRaisesRegex(ValueError, "wrong number"):
            DenseRetriever(self.chunks, type("WrongCount", (), {"encode": lambda self, _: [[1, 0]]})())

    def test_rejects_bad_query_vectors(self):
        index = DenseRetriever(self.chunks, FakeEncoder({**self.vectors, "bad": [1, 2, 3]}))
        with self.assertRaisesRegex(ValueError, "dimensions"):
            index.search("bad")
        index.encoder = type("WrongCount", (), {"encode": lambda self, _: []})()
        with self.assertRaisesRegex(ValueError, "exactly one"):
            index.search("bad")

    def test_cli_benchmark_uses_dense_and_records_fingerprints(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sources").mkdir()
            (root / "examples").mkdir()
            (root / "sources/manifest.json").write_text('{"sources": []}', encoding="utf-8")
            (root / "examples/labels.json").write_text(json.dumps({"queries": [
                {"question": "investigator analyzed material", "relevant_sources": ["beta"]}
            ]}), encoding="utf-8")
            output = io.StringIO()
            with patch("evidenceflip.rag_cli.load_sources", return_value=[
                Source("alpha", self.chunks[0].text), Source("beta", self.chunks[1].text)
            ]), patch("evidenceflip.rag_cli.SentenceTransformerEncoder", return_value=FakeEncoder(self.vectors)):
                with redirect_stdout(output):
                    code = main(["--root", str(root), "--retriever", "dense", "benchmark",
                                 "--set", "examples/labels.json", "--top-k", "1"])
            self.assertEqual(code, 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["hit_rate"], 1.0)
            self.assertEqual(result["configuration"]["retriever"], "dense")
            self.assertEqual(result["configuration"]["embedding_model"], "sentence-transformers/all-MiniLM-L6-v2")
            self.assertEqual(result["configuration"]["source_manifest_sha256"],
                             hashlib.sha256((root / "sources/manifest.json").read_bytes()).hexdigest())
            self.assertEqual(len(result["configuration"]["benchmark_sha256"]), 64)
            self.assertGreaterEqual(result["retrieval_elapsed_ms"], 0)

    def test_missing_optional_dependency_is_actionable(self):
        with patch.dict("sys.modules", {"sentence_transformers": None}):
            with self.assertRaisesRegex(RuntimeError, r"\[dense\]"):
                SentenceTransformerEncoder()


if __name__ == "__main__":
    unittest.main()
