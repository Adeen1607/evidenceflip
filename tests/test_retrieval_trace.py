"""Synthetic MIT-licensed fixtures for deterministic BM25 retrieval replay."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from evidenceflip.retrieval_trace import capture_bm25_trace, evaluate_trace_bound_annotations


class RetrievalTraceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "sources").mkdir()
        content = "Alpha beta gamma delta epsilon zeta."
        (self.root / "sources" / "example.txt").write_text(content, encoding="utf-8")
        (self.root / "sources" / "manifest.json").write_text(json.dumps({"sources": [{
            "id": "example", "path": "sources/example.txt", "title": "Synthetic fixture",
            "license": "MIT", "origin": "project-authored synthetic fixture",
            "sha256": hashlib.sha256(content.encode()).hexdigest()
        }]}), encoding="utf-8")
        self.trace = capture_bm25_trace("alpha", self.root, chunk_size=3, overlap=0, top_k=1)
        self.row = {
            "id": "a", "claim": "Alpha beta", "retrieved_source_ids": ["example"],
            "evidence_passages": {"example": "Alpha beta"},
            "retrieval_chunks": {"example": {
                "chunk_id": "example#w0", "start_word": 0, "end_word": 3,
                "passage": "Alpha beta"}},
            "gold": "supported", "predicted": "supported",
            "retrieval_trace": self.trace,
        }

    def evaluate(self, row=None):
        return evaluate_trace_bound_annotations([row or self.row], self.root,
                                                chunk_size=3, overlap=0)

    def test_valid_replay(self):
        result = self.evaluate()
        self.assertTrue(result["retrieval_replay_verified"])
        self.assertEqual(result["tp"], 1)

    def test_fabricated_ranking_rejected(self):
        row = copy.deepcopy(self.row)
        row["retrieval_trace"]["hits"][0]["score"] = 99
        with self.assertRaisesRegex(ValueError, "differs"):
            self.evaluate(row)

    def test_nonreturned_chunk_rejected(self):
        row = copy.deepcopy(self.row)
        row["retrieval_chunks"]["example"] = {
            "chunk_id": "example#w3", "start_word": 3, "end_word": 6,
            "passage": "delta epsilon"}
        row["evidence_passages"]["example"] = "delta epsilon"
        with self.assertRaisesRegex(ValueError, "not returned"):
            self.evaluate(row)

    def test_tampered_source_rejected(self):
        (self.root / "sources" / "example.txt").write_text("altered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            self.evaluate()

    def test_malformed_trace_rejected(self):
        row = copy.deepcopy(self.row)
        row["retrieval_trace"].pop("top_k")
        with self.assertRaisesRegex(ValueError, "Malformed"):
            self.evaluate(row)

    def test_wrong_query_rejected(self):
        row = copy.deepcopy(self.row)
        row["retrieval_trace"]["question"] = "zeta"
        with self.assertRaisesRegex(ValueError, "differs"):
            self.evaluate(row)

    def test_invalid_top_k_rejected(self):
        for value in (0, True, 1.5):
            with self.subTest(value=value), self.assertRaises(ValueError):
                capture_bm25_trace("alpha", self.root, top_k=value)

    def test_chunk_configuration_mismatch(self):
        row = copy.deepcopy(self.row)
        row["retrieval_trace"]["chunk_size"] = 5
        with self.assertRaisesRegex(ValueError, "settings mismatch"):
            self.evaluate(row)


if __name__ == "__main__":
    unittest.main()
