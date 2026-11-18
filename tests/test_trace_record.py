"""MIT-licensed project-authored synthetic tests for versioned trace records."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from evidenceflip.retrieval_trace import capture_bm25_trace
from evidenceflip.trace_record import (
    canonical_bytes, runtime_metadata, seal_trace, verify_trace_record,
)


class TraceRecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "sources").mkdir()
        data = "alpha beta gamma delta"
        (self.root / "sources" / "example.txt").write_text(data, encoding="utf-8")
        (self.root / "sources" / "manifest.json").write_text(json.dumps({"sources": [{
            "id": "example", "path": "sources/example.txt", "title": "Synthetic example",
            "license": "MIT", "origin": "project-authored synthetic fixture",
            "sha256": hashlib.sha256(data.encode()).hexdigest()
        }]}), encoding="utf-8")
        self.trace = capture_bm25_trace("alpha", self.root, chunk_size=2, overlap=0)
        self.record = seal_trace(self.trace)

    def test_roundtrip_json_and_replay(self):
        record = json.loads(json.dumps(self.record))
        result = verify_trace_record(record, self.root)
        self.assertTrue(result["record_verified"])
        self.assertTrue(result["environment_matches"])

    def test_canonical_encoding_ignores_key_order(self):
        self.assertEqual(canonical_bytes({"b": 2, "a": 1}),
                         canonical_bytes({"a": 1, "b": 2}))

    def test_modified_hit_rejected_by_digest(self):
        record = copy.deepcopy(self.record)
        record["trace"]["hits"][0]["score"] = 99
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_trace_record(record, self.root)

    def test_resealed_forgery_fails_replay(self):
        trace = copy.deepcopy(self.trace)
        trace["hits"][0]["score"] = 99
        with self.assertRaisesRegex(ValueError, "differs"):
            verify_trace_record(seal_trace(trace), self.root)

    def test_tampered_corpus_rejected(self):
        (self.root / "sources" / "example.txt").write_text("altered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            verify_trace_record(self.record, self.root)

    def test_schema_and_digest_validation(self):
        for key, value in (("schema", "unknown"), ("sha256", "z" * 64)):
            record = copy.deepcopy(self.record)
            record[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_trace_record(record, self.root)

    def test_unknown_fields_rejected(self):
        record = copy.deepcopy(self.record)
        record["untrusted"] = "extra"
        with self.assertRaisesRegex(ValueError, "Malformed"):
            verify_trace_record(record, self.root)

    def test_nonfinite_and_nonjson_rejected(self):
        for value in (float("nan"), float("inf"), object()):
            with self.subTest(value=str(value)), self.assertRaises(ValueError):
                canonical_bytes({"bad": value})

    def test_v1_records_remain_readable(self):
        record = {"schema": "evidenceflip.trace_record.v1", "trace": self.trace,
                  "sha256": hashlib.sha256(canonical_bytes(self.trace)).hexdigest()}
        result = verify_trace_record(record, self.root)
        self.assertTrue(result["record_verified"])
        self.assertIsNone(result["environment_matches"])

    def test_metadata_changes_invalidate_digest(self):
        record = copy.deepcopy(self.record)
        record["metadata"]["package_version"] = "forged"
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            verify_trace_record(record, self.root)

    def test_resealed_other_environment_is_visible_not_rejected(self):
        metadata = dict(runtime_metadata())
        metadata["python_version"] = "3.10.0"
        record = seal_trace(self.trace, metadata=metadata)
        result = verify_trace_record(record, self.root)
        self.assertTrue(result["record_verified"])
        self.assertFalse(result["environment_matches"])

    def test_invalid_metadata_rejected(self):
        for metadata in ({"package_version": "1"}, dict(runtime_metadata(), retriever="dense"),
                         dict(runtime_metadata(), python_version="")):
            with self.subTest(metadata=metadata), self.assertRaises(ValueError):
                seal_trace(self.trace, metadata=metadata)

    def test_metadata_is_stable_in_canonical_record(self):
        metadata = dict(runtime_metadata())
        record = seal_trace(self.trace, metadata=metadata)
        self.assertEqual(record["sha256"], seal_trace(self.trace, metadata=metadata)["sha256"])


if __name__ == "__main__":
    unittest.main()
