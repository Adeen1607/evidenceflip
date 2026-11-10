import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from evidenceflip.ingest import register_source
from evidenceflip.rag import load_sources

class SourceIngestionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        (self.root / "sources").mkdir()
        (self.root / "sources/manifest.json").write_text(json.dumps({"schema_version": 1, "sources": []}),encoding="utf-8")
        self.input = self.root / "study.md"
        self.input.write_text("# A self-authored result\n\nWe used five controlled trials.",encoding="utf-8")

    def tearDown(self):
        self.directory.cleanup()

    def test_register_load_and_retrieve(self):
        entry=register_source(self.root,self.input,"study",title="Study",origin="author-generated",license="MIT")
        self.assertEqual(entry["path"],"sources/imported/study.md")
        self.assertEqual(entry["sha256"],hashlib.sha256(self.input.read_bytes()).hexdigest())
        self.assertEqual(load_sources(self.root)[0].text,self.input.read_text())

    def test_reject_duplicate_source_id(self):
        for n in range(2):
            if n==1:
                with self.assertRaisesRegex(ValueError,"already registered"):
                    register_source(self.root,self.input,"study",title="Study",origin="author",license="MIT")
            else:
                register_source(self.root,self.input,"study",title="Study",origin="author",license="MIT")

    def test_reject_unsafe_id_and_unknown_license(self):
        with self.assertRaises(ValueError):
            register_source(self.root,self.input,"../../secrets",title="Study",origin="author",license="MIT")
        with self.assertRaises(ValueError):
            register_source(self.root,self.input,"safe",title="Study",origin="author",license="")

    def test_modified_import_fails_integrity_check(self):
        entry=register_source(self.root,self.input,"study",title="Study",origin="author",license="MIT")
        (self.root/entry["path"]).write_text("modified",encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"integrity mismatch"):
            load_sources(self.root)

if __name__ == "__main__":
    unittest.main()
