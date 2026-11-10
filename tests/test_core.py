"""Regression tests for EvidenceFlip's DATA INTEGRITY contract."""
from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from evidenceflip.agents import policy_agent
from evidenceflip.cli import load_scenarios, main
from evidenceflip.core import Answer, Evidence, Scenario, compare, evaluate, verify_registry

ROOT = Path(__file__).resolve().parents[1]
QUESTION = "How many days do customers have to request a refund?"
POLICY = Evidence("refund-policy", "The refund window is 30 days from purchase.")
SUPPORT = Evidence("customer-support", "Customers can contact support by email.")


class DataIntegrityTests(unittest.TestCase):
    def test_registered_examples_are_unchanged(self):
        results = verify_registry(ROOT)
        self.assertGreaterEqual(len(results), 2)
        self.assertTrue(all(item["valid"] for item in results), results)

    def test_modified_file_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "sources" / "articles"
            source.mkdir(parents=True)
            original = b"The refund window is 30 days."
            (source / "policy.md").write_bytes(original)
            manifest = {"sources": [{"id": "policy", "path": "sources/articles/policy.md",
                                     "sha256": hashlib.sha256(original).hexdigest()}]}
            (root / "sources" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertTrue(verify_registry(root)[0]["valid"])
            (source / "policy.md").write_bytes(b"The refund window is 365 days.")
            self.assertFalse(verify_registry(root)[0]["valid"])

    def test_missing_source_fails_verification(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sources").mkdir()
            (root / "sources" / "manifest.json").write_text(
                json.dumps({"sources": [{"id": "missing", "path": "sources/not-there.md", "sha256": "0" * 64}]}),
                encoding="utf-8",
            )
            outcome = verify_registry(root)[0]
            self.assertFalse(outcome["valid"])
            self.assertEqual(outcome["reason"], "missing")

    def test_source_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sources").mkdir()
            (root / "sources" / "manifest.json").write_text(
                json.dumps({"sources": [{"id": "bad", "path": "../escape.md", "sha256": "0" * 64}]}),
                encoding="utf-8",
            )
            # Path is relative to repository root. The negative case must leave that root.
            (root / "sources" / "manifest.json").write_text(
                json.dumps({"sources": [{"id": "bad", "path": "../escape.md", "sha256": "0" * 64}]}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                verify_registry(root)

    def test_baseline_answer_and_citation(self):
        scenario = Scenario("baseline", QUESTION, (POLICY, SUPPORT),
                            expected_text="30 days", expected_citations=("refund-policy",))
        result = evaluate(scenario, policy_agent)
        self.assertTrue(result.passed)
        self.assertTrue(all(result.checks.values()))

    def test_policy_removal_causes_abstention(self):
        scenario = Scenario("removed", QUESTION, (SUPPORT,),
                            expected_text="cannot determine",
                            expected_citations=(), expect_abstention=True)
        result = evaluate(scenario, policy_agent)
        self.assertTrue(result.passed)
        self.assertEqual(result.citations, ())

    def test_policy_replacement_changes_answer(self):
        changed = Evidence("refund-policy", "The refund window is 14 days from purchase.")
        baseline = evaluate(Scenario("baseline", QUESTION, (POLICY,)), policy_agent)
        result = evaluate(Scenario("replacement", QUESTION, (changed,), expected_text="14 days"), policy_agent)
        self.assertTrue(compare(baseline, result, should_change=True)["passed"])

    def test_irrelevant_source_negative_control_is_stable(self):
        baseline = evaluate(Scenario("baseline", QUESTION, (POLICY, SUPPORT)), policy_agent)
        control = evaluate(Scenario("control", QUESTION, (POLICY,)), policy_agent)
        self.assertTrue(compare(baseline, control, should_change=False)["passed"])

    def test_fabricated_citation_fails(self):
        def invalid_agent(question, evidence):
            return Answer("30 days", ("made-up-source",))
        result = evaluate(Scenario("invalid citation", QUESTION, (POLICY,)), invalid_agent)
        self.assertFalse(result.passed)
        self.assertFalse(result.checks["citations_available"])

    def test_duplicate_evidence_identifiers_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            evaluate(Scenario("duplicate", QUESTION, (POLICY, POLICY)), policy_agent)

    def test_expected_answer_check_can_fail(self):
        result = evaluate(Scenario("expect wrong", QUESTION, (POLICY,), expected_text="365 days"), policy_agent)
        self.assertFalse(result.passed)
        self.assertFalse(result.checks["expected_text"])

    def test_demo_case_suite_loads_and_passes(self):
        scenarios = load_scenarios(ROOT / "examples" / "refund_scenarios.json")
        self.assertEqual(len(scenarios), 4)
        results = [evaluate(s, policy_agent) for s in scenarios]
        self.assertTrue(all(r.passed for r in results), results)

    def test_cli_verify_and_demo(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(["verify", "--root", str(ROOT)]), 0)
            self.assertEqual(main(["demo"]), 0)

    def test_cli_produces_json_report(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "evaluation.json"
            with redirect_stdout(io.StringIO()):
                code = main(["demo", "--output", str(output)])
            self.assertEqual(code, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["summary"], {"total": 4, "passed": 4})
            self.assertEqual(len(report["results"]), 4)


if __name__ == "__main__":
    unittest.main()
