"""Offline regression tests for provenance-bound annotation evaluation."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from evidenceflip.support_eval import evaluate_bound_annotations


class BoundSupportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "sources").mkdir()
        self.text = "Alpha is a synthetic observation. Beta is an example."
        (self.root / "sources" / "example.txt").write_text(self.text, encoding="utf-8")
        self.manifest = {"sources": [{
            "id": "example", "path": "sources/example.txt",
            "title": "Project-authored synthetic example",
            "license": "MIT",
            "sha256": hashlib.sha256(self.text.encode()).hexdigest()
        }]}
        (self.root / "sources" / "manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8")
        self.row = {"id": "claim-1", "claim": "Alpha is a synthetic observation.",
                    "retrieved_source_ids": ["example"],
                    "evidence_passages": {"example": "Alpha is a synthetic observation."},
                    "gold": "supported", "predicted": "supported"}

    def test_valid_exact_passage(self):
        report = evaluate_bound_annotations([self.row], self.root)
        self.assertTrue(report["provenance_verified"])
        self.assertEqual(report["tp"], 1)

    def test_unknown_source_rejected(self):
        row = {**self.row, "retrieved_source_ids": ["missing"],
               "evidence_passages": {"missing": "Alpha"}}
        with self.assertRaisesRegex(ValueError, "Unknown manifest source"):
            evaluate_bound_annotations([row], self.root)

    def test_mismatched_or_empty_passages_rejected(self):
        for passages in ({}, {"example": ""}, {"example": "Alpha", "extra": "Beta"},
                         {"example": 4}):
            with self.subTest(passages=passages), self.assertRaises(ValueError):
                evaluate_bound_annotations([{**self.row, "evidence_passages": passages}], self.root)

    def test_nonexistent_passage_rejected(self):
        row = {**self.row, "evidence_passages": {"example": "Invented fact"}}
        with self.assertRaisesRegex(ValueError, "not found"):
            evaluate_bound_annotations([row], self.root)

    def test_tampering_detected(self):
        (self.root / "sources" / "example.txt").write_text(self.text + " changed", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            evaluate_bound_annotations([self.row], self.root)

    def test_duplicate_and_invalid_labels_still_rejected(self):
        for rows in ([self.row, self.row],
                     [{**self.row, "gold": "uncertain"}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                evaluate_bound_annotations(rows, self.root)


if __name__ == "__main__":
    unittest.main()
