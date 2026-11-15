"""Offline chunk binding regression tests using project-authored synthetic text."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from evidenceflip.chunk_support import evaluate_chunk_bound_annotations


class ChunkBoundSupportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "sources").mkdir()
        self.text = "Alpha beta gamma delta epsilon zeta."
        (self.root / "sources" / "example.txt").write_text(self.text, encoding="utf-8")
        (self.root / "sources" / "manifest.json").write_text(json.dumps({"sources": [{
            "id": "example", "path": "sources/example.txt",
            "title": "Synthetic test fixture", "license": "MIT",
            "sha256": hashlib.sha256(self.text.encode()).hexdigest()
        }]}), encoding="utf-8")
        self.row = {
            "id": "claim-1", "claim": "Alpha beta",
            "retrieved_source_ids": ["example"],
            "evidence_passages": {"example": "Alpha beta"},
            "retrieval_chunks": {"example": {
                "chunk_id": "example#w0", "start_word": 0, "end_word": 3,
                "passage": "Alpha beta"}},
            "gold": "supported", "predicted": "supported",
        }

    def evaluate(self, row=None):
        return evaluate_chunk_bound_annotations(
            [self.row if row is None else row], self.root, chunk_size=3, overlap=0)

    def test_valid_chunk_and_metrics(self):
        report = self.evaluate()
        self.assertTrue(report["chunk_provenance_verified"])
        self.assertEqual(report["tp"], 1)

    def test_unknown_chunk_rejected(self):
        item = {**self.row["retrieval_chunks"]["example"], "chunk_id": "example#w99"}
        with self.assertRaisesRegex(ValueError, "Unknown chunk"):
            self.evaluate({**self.row, "retrieval_chunks": {"example": item}})

    def test_wrong_source_or_offset_rejected(self):
        for change in ({"chunk_id": "example#w3"}, {"end_word": 4},
                       {"start_word": True}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                item = {**self.row["retrieval_chunks"]["example"], **change}
                self.evaluate({**self.row, "retrieval_chunks": {"example": item}})

    def test_passage_outside_retrieved_chunk_rejected(self):
        row = {**self.row, "evidence_passages": {"example": "epsilon zeta"},
               "retrieval_chunks": {"example": {
                   **self.row["retrieval_chunks"]["example"],
                   "passage": "epsilon zeta"}}}
        with self.assertRaisesRegex(ValueError, "not bound to chunk"):
            self.evaluate(row)

    def test_mismatched_passage_and_missing_binding_rejected(self):
        for binding in ({}, {"example": {
            **self.row["retrieval_chunks"]["example"], "passage": "beta gamma"
        }}):
            with self.subTest(binding=binding), self.assertRaises(ValueError):
                self.evaluate({**self.row, "retrieval_chunks": binding})

    def test_source_tampering_rejected(self):
        (self.root / "sources" / "example.txt").write_text(
            self.text + " tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            self.evaluate()

    def test_invalid_chunk_parameters_rejected(self):
        with self.assertRaises(ValueError):
            evaluate_chunk_bound_annotations([self.row], self.root, chunk_size=2, overlap=2)


if __name__ == "__main__":
    unittest.main()
