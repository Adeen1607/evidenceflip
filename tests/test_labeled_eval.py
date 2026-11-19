"""Project-authored MIT-licensed synthetic retrieval relevance fixtures."""
import unittest
from types import SimpleNamespace

from evidenceflip.labeled_eval import evaluate_ranked_sources, collect_ranked_sources


class LabeledEvaluationTests(unittest.TestCase):
    def test_metrics_with_multiple_relevant_sources(self):
        result = evaluate_ranked_sources([
            {"id": "q1", "question": "Alpha?", "relevant_sources": ["a", "b"],
             "retrieved_sources": ["x", "a", "b"]},
            {"id": "q2", "question": "Beta?", "relevant_sources": ["b"],
             "retrieved_sources": ["x"]},
        ], k=2, known_sources=["a", "b", "x"])
        self.assertEqual(result["hit_rate"], .5)
        self.assertEqual(result["mrr"], .25)
        self.assertEqual(result["precision_at_k"], .25)
        self.assertEqual(result["recall_at_k"], .25)

    def test_empty_retrieval_is_valid_miss(self):
        result = evaluate_ranked_sources([
            {"id": "1", "question": "Missing?", "relevant_sources": ["a"],
             "retrieved_sources": []}
        ])
        self.assertEqual(result["mrr"], 0)
        self.assertEqual(result["recall_at_k"], 0)

    def test_first_rank_and_top_k_cutoff(self):
        case = {"id": "1", "question": "A?", "relevant_sources": ["a"],
                "retrieved_sources": ["a", "x"]}
        self.assertEqual(evaluate_ranked_sources([case], k=1)["mrr"], 1)
        case["retrieved_sources"] = ["x", "a"]
        self.assertEqual(evaluate_ranked_sources([case], k=1)["hit_rate"], 0)

    def test_reject_duplicate_questions_after_normalization(self):
        cases = [
            {"id": "1", "question": "  Refund   Policy ", "relevant_sources": ["a"],
             "retrieved_sources": []},
            {"id": "2", "question": "refund policy", "relevant_sources": ["a"],
             "retrieved_sources": []},
        ]
        with self.assertRaisesRegex(ValueError, "leakage"):
            evaluate_ranked_sources(cases)

    def test_reject_duplicate_ids_and_relevance(self):
        case = {"id": "1", "question": "A?", "relevant_sources": ["a", "a"],
                "retrieved_sources": []}
        with self.assertRaisesRegex(ValueError, "Duplicate relevant"):
            evaluate_ranked_sources([case])
        case["relevant_sources"] = ["a"]
        with self.assertRaisesRegex(ValueError, "Case IDs"):
            evaluate_ranked_sources([case, dict(case, question="B?")])

    def test_reject_unknown_sources_and_invalid_k(self):
        case = {"id": "1", "question": "A?", "relevant_sources": ["a"],
                "retrieved_sources": ["unknown"]}
        with self.assertRaisesRegex(ValueError, "Unknown retrieved"):
            evaluate_ranked_sources([case], known_sources=["a"])
        with self.assertRaises(ValueError):
            evaluate_ranked_sources([case], k=True)

    def test_reject_malformed_labels(self):
        case = {"id": "1", "question": "A?", "relevant_sources": [],
                "retrieved_sources": []}
        with self.assertRaises(ValueError):
            evaluate_ranked_sources([case])
        with self.assertRaises(ValueError):
            evaluate_ranked_sources([dict(case, relevant_sources=["a"], extra=1)])

    def test_adapter_deduplicates_chunks_and_preserves_order(self):
        class FakeRetriever:
            def search(self, question, top_k):
                self.request = (question, top_k)
                return [SimpleNamespace(chunk=SimpleNamespace(source_id=s))
                        for s in ("a", "a", "b")]
        retriever = FakeRetriever()
        self.assertEqual(collect_ranked_sources(retriever, "Question", k=3), ["a", "b"])
        self.assertEqual(retriever.request, ("Question", 3))

    def test_adapter_rejects_invalid_input_and_output(self):
        class BadRetriever:
            def search(self, question, top_k):
                return [SimpleNamespace(chunk=SimpleNamespace(source_id=""))]
        with self.assertRaises(ValueError):
            collect_ranked_sources(BadRetriever(), "A?")
        with self.assertRaises(ValueError):
            collect_ranked_sources(BadRetriever(), " ")
        with self.assertRaises(ValueError):
            collect_ranked_sources(BadRetriever(), "A?", k=0)


if __name__ == "__main__":
    unittest.main()
