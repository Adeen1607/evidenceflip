"""Offline tests for manually annotated claim-support evaluation."""
import json
import tempfile
import unittest
from pathlib import Path
from evidenceflip.support_eval import evaluate_annotations, evaluate_file


def row(i, gold, predicted):
    return {"id": str(i), "claim": "Example claim", "retrieved_source_ids": ["example"],
            "gold": gold, "predicted": predicted}


class SupportEvaluationTests(unittest.TestCase):
    def test_confusion_and_metrics(self):
        data = [row(1, "supported", "supported"), row(2, "unsupported", "supported"),
                row(3, "supported", "unsupported"), row(4, "unsupported", "unsupported")]
        report = evaluate_annotations(data)
        self.assertEqual(tuple(report[k] for k in ("tp", "fp", "fn", "tn")), (1, 1, 1, 1))
        self.assertEqual((report["precision"], report["recall"], report["f1"]), (0.5, 0.5, 0.5))

    def test_abstentions_excluded(self):
        report = evaluate_annotations([row(1, "unanswerable", "supported"),
                                       row(2, "supported", "unanswerable")])
        self.assertEqual(report["scored"], 0)
        self.assertEqual(report["excluded_unanswerable_gold"], 1)
        self.assertEqual(report["predicted_abstentions"], 1)
        self.assertIsNone(report["precision"])

    def test_no_positive_predictions_not_perfect(self):
        report = evaluate_annotations([row(1, "unsupported", "unsupported")])
        self.assertIsNone(report["precision"])
        self.assertIsNone(report["recall"])
        self.assertIsNone(report["f1"])

    def test_invalid_rows(self):
        for data in ([], [row(1, "supported", "supported")] * 2,
                     [row(1, "maybe", "supported")],
                     [{**row(1, "supported", "supported"), "retrieved_source_ids": []}],
                     [{**row(1, "supported", "supported"), "claim": " "}]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                evaluate_annotations(data)

    def test_json_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "labels.json"
            path.write_text(json.dumps([row(1, "supported", "supported")]), encoding="utf-8")
            self.assertEqual(evaluate_file(path)["tp"], 1)


if __name__ == "__main__":
    unittest.main()
