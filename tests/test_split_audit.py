"""MIT-licensed project-authored synthetic split-audit regression cases."""
import unittest

from evidenceflip.split_audit import audit_question_splits, require_disjoint_question_splits


class SplitAuditTests(unittest.TestCase):
    def test_disjoint(self):
        result = require_disjoint_question_splits({
            "development": [{"id": "d1", "question": "What is alpha?"}],
            "test": [{"id": "t1", "question": "What is beta?"}],
        })
        self.assertTrue(result["disjoint"])
        self.assertEqual(result["split_sizes"], {"development": 1, "test": 1})

    def test_normalized_question_overlap(self):
        splits = {"dev": [{"id": "a", "question": "  REFUND   policy "}],
                  "test": [{"id": "b", "question": "refund policy"}]}
        result = audit_question_splits(splits)
        self.assertFalse(result["disjoint"])
        self.assertEqual(result["question_overlaps"][0]["splits"], ["dev", "test"])
        self.assertEqual(len(result["question_overlaps"][0]["question_sha256"]), 64)
        self.assertNotIn("refund policy", str(result["question_overlaps"]))
        with self.assertRaisesRegex(ValueError, "overlap"):
            require_disjoint_question_splits(splits)

    def test_repeated_id_across_splits(self):
        result = audit_question_splits({
            "dev": [{"id": "same", "question": "A"}],
            "test": [{"id": "same", "question": "B"}],
        })
        self.assertEqual(result["case_id_overlaps"], [{"id": "same", "splits": ["dev", "test"]}])

    def test_reject_within_split_duplicates(self):
        with self.assertRaisesRegex(ValueError, "Duplicate normalized"):
            audit_question_splits({
                "dev": [{"id": "a", "question": " A "}, {"id": "b", "question": "a"}],
                "test": [{"id": "c", "question": "C"}],
            })
        with self.assertRaisesRegex(ValueError, "Duplicate case ID"):
            audit_question_splits({
                "dev": [{"id": "a", "question": "A"}, {"id": "a", "question": "B"}],
                "test": [{"id": "c", "question": "C"}],
            })

    def test_invalid_schema(self):
        invalid = [
            {}, {"dev": []}, {"dev": [], "test": [{"id": "t", "question": "T"}]},
            {"dev": [{"id": "d", "question": " "}], "test": [{"id": "t", "question": "T"}]},
            {"dev": [{"question": "A"}], "test": [{"id": "t", "question": "T"}]},
            {"dev": [{"id": 1, "question": "A"}], "test": [{"id": "t", "question": "T"}]},
            {"dev": "bad", "test": [{"id": "t", "question": "T"}]},
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit_question_splits(value)

    def test_permits_relevance_fields(self):
        result = require_disjoint_question_splits({
            "dev": [{"id": "d", "question": "A", "relevant_sources": ["s"]}],
            "test": [{"id": "t", "question": "B", "retrieved_sources": []}],
        })
        self.assertTrue(result["disjoint"])


if __name__ == "__main__":
    unittest.main()
