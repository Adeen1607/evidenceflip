"""MIT-licensed synthetic offline tests for the benchmark runner."""
import unittest
from types import SimpleNamespace

from evidenceflip.benchmark_runner import run_labeled_benchmark


class Retriever:
    def __init__(self, sources):
        self.sources = sources
        self.calls = []

    def search(self, question, top_k):
        self.calls.append((question, top_k))
        return [SimpleNamespace(chunk=SimpleNamespace(source_id=s))
                for s in self.sources[:top_k]]


class BenchmarkRunnerTests(unittest.TestCase):
    def setUp(self):
        self.splits = {
            "development": [{"id": "dev", "question": "What is alpha?"}],
            "test": [{"id": "test", "question": "Where is beta?",
                      "relevant_sources": ["b"]}],
        }

    def test_compares_same_queries_and_measures_actual_calls(self):
        first, second = Retriever(["a", "b"]), Retriever(["b", "a"])
        report = run_labeled_benchmark(self.splits, {"lexical": first, "dense_mock": second},
                                       known_sources=["a", "b"], k=2)
        self.assertEqual(first.calls, [("Where is beta?", 2)])
        self.assertEqual(second.calls, first.calls)
        self.assertEqual(report["retrievers"]["lexical"]["metrics"]["mrr"], .5)
        self.assertEqual(report["retrievers"]["dense_mock"]["metrics"]["mrr"], 1)
        self.assertGreaterEqual(report["retrievers"]["lexical"]["latency_ms"]["mean"], 0)
        self.assertTrue(report["split_audit"]["disjoint"])

    def test_duplicate_chunks_do_not_count_as_distinct_sources(self):
        result = run_labeled_benchmark(self.splits, {"mock": Retriever(["a", "a"])},
                                       known_sources=["a", "b"], k=2)
        self.assertEqual(result["retrievers"]["mock"]["metrics"]["recall_at_k"], 0)

    def test_rejects_leakage_before_search(self):
        retriever = Retriever(["b"])
        self.splits["development"][0]["question"] = " WHERE is BETA? "
        with self.assertRaisesRegex(ValueError, "overlap"):
            run_labeled_benchmark(self.splits, {"mock": retriever}, known_sources=["b"])
        self.assertEqual(retriever.calls, [])

    def test_rejects_unknown_labels_before_search(self):
        retriever = Retriever(["b"])
        with self.assertRaisesRegex(ValueError, "Unknown relevant"):
            run_labeled_benchmark(self.splits, {"mock": retriever}, known_sources=["a"])
        self.assertEqual(retriever.calls, [])

    def test_rejects_invalid_configuration(self):
        with self.assertRaises(ValueError):
            run_labeled_benchmark(self.splits, {}, known_sources=["b"])
        with self.assertRaises(ValueError):
            run_labeled_benchmark(self.splits, {"mock": Retriever(["b"])},
                                  known_sources=["b"], k=True)
        with self.assertRaises(ValueError):
            run_labeled_benchmark(self.splits, {"mock": object()}, known_sources=["b"])
        with self.assertRaises(ValueError):
            run_labeled_benchmark(self.splits, {"mock": Retriever(["b"])},
                                  known_sources=["b", "b"])

    def test_rejects_unknown_retrieved_sources(self):
        with self.assertRaisesRegex(ValueError, "Unknown retrieved"):
            run_labeled_benchmark(self.splits, {"mock": Retriever(["fabricated"])},
                                  known_sources=["b"])

    def test_invalid_later_retriever_does_not_run_first(self):
        first = Retriever(["b"])
        with self.assertRaisesRegex(ValueError, "broken"):
            run_labeled_benchmark(
                self.splits, {"first": first, "broken": object()},
                known_sources=["b"],
            )
        self.assertEqual(first.calls, [])

    def test_noncallable_search_does_not_run_first(self):
        first = Retriever(["b"])
        broken = SimpleNamespace(search=None)
        with self.assertRaisesRegex(ValueError, "broken"):
            run_labeled_benchmark(
                self.splits, {"first": first, "broken": broken},
                known_sources=["b"],
            )
        self.assertEqual(first.calls, [])

    def test_valid_adapters_still_execute_in_order(self):
        first, second = Retriever(["a"]), Retriever(["b"])
        report = run_labeled_benchmark(
            self.splits, {"first": first, "second": second},
            known_sources=["a", "b"], k=1,
        )
        self.assertEqual(list(report["retrievers"]), ["first", "second"])
        self.assertEqual(first.calls, second.calls)
        self.assertEqual(report["retrievers"]["second"]["metrics"]["hit_rate"], 1)


if __name__ == "__main__":
    unittest.main()
