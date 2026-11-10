import re
import unittest
from evidenceflip.core import Evidence
from evidenceflip.rag_adapter import make_rag_agent

class CounterfactualAdapterTests(unittest.TestCase):
    def test_source_replacement_propagates_to_retrieval_and_generator(self):
        def fake_llm(prompt):
            match = re.search(r"refund window is (\d+) days", prompt, re.IGNORECASE)
            return (f"The window is {match.group(1)} days. [refund-policy]"
                    if match else "Insufficient evidence")
        agent = make_rag_agent(fake_llm)
        original = agent("How long is the refund window?", (Evidence("refund-policy", "The refund window is 30 days."),))
        changed = agent("How long is the refund window?", (Evidence("refund-policy", "The refund window is 14 days."),))
        removed = agent("How long is the refund window?", ())
        self.assertIn("30 days", original.text)
        self.assertIn("14 days", changed.text)
        self.assertEqual(changed.citations, ("refund-policy",))
        self.assertIn("Insufficient evidence", removed.text)

    def test_invented_citation_is_preserved(self):
        agent = make_rag_agent(lambda _: "A refund is 30 days [invented]")
        result = agent("refund window", (Evidence("refund-policy", "refund window is 30 days"),))
        self.assertEqual(result.citations, ("invented",))

if __name__ == "__main__":
    unittest.main()
