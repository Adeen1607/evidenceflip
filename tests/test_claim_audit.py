"""Offline acceptance tests for conservative claim citation coverage."""
import unittest

from evidenceflip.claim_audit import audit_answer, audit_result
from evidenceflip.rag import Chunk, Hit, RAGResult


class ClaimCitationAuditTests(unittest.TestCase):
    def test_covered_and_uncited_claims(self):
        report = audit_answer("Orion has 480 records [dataset-card]. Another claim.", ["dataset-card"])
        self.assertEqual(report["claims_total"], 2)
        self.assertEqual(report["claims_with_retrieved_citation"], 1)
        self.assertEqual(report["citation_coverage"], 0.5)
        self.assertEqual(report["uncited_claims"], ["Another claim."])

    def test_invented_source_is_not_coverage(self):
        report = audit_answer("A result [invented].", ["dataset-card"])
        self.assertEqual(report["citation_coverage"], 0)
        self.assertEqual(report["unknown_citation_claims"], ["A result [invented]."])
        self.assertEqual(report["uncited_claims"], [])

    def test_multiple_citations_and_duplicate_ids(self):
        report = audit_answer("One [a] [a] [fake].", ["a"])
        claim = report["claims"][0]
        self.assertEqual(claim["cited_sources"], ("a", "fake"))
        self.assertEqual(claim["retrieved_citations"], ("a",))
        self.assertEqual(claim["unknown_citations"], ("fake",))

    def test_abstention_not_a_factual_claim(self):
        report = audit_answer("Insufficient evidence.", [])
        self.assertEqual(report["claims_total"], 0)
        self.assertIsNone(report["citation_coverage"])

    def test_no_evidence_does_not_mean_valid_citation(self):
        report = audit_answer("A factual claim [policy].", [])
        self.assertEqual(report["claims_with_retrieved_citation"], 0)

    def test_audit_pipeline_result_uses_only_retrieved_sources(self):
        chunk = Chunk("dataset-card#w0", "dataset-card", "480 records", 0, 2)
        result = RAGResult("How many?", "480 records [dataset-card].", ("dataset-card",),
                           (), (Hit(chunk, 1.0),), 1.0, "mock")
        self.assertEqual(audit_result(result)["citation_coverage"], 1)

    def test_blank_and_invalid_ids_rejected(self):
        with self.assertRaises(ValueError):
            audit_answer("  ", ["a"])
        with self.assertRaises(ValueError):
            audit_answer("Claim.", [""])

    def test_no_entailment_claim(self):
        report = audit_answer("Orion has a billion records [dataset-card].", ["dataset-card"])
        self.assertEqual(report["citation_coverage"], 1)
        self.assertIn("not entailment", report["warning"])


if __name__ == "__main__":
    unittest.main()
