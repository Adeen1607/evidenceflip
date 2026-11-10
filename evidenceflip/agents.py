"""Reference adapter for a deterministic, inspectable demo. Not an LLM."""
import re
from .core import Answer, Evidence

def policy_agent(question: str, evidence: tuple[Evidence, ...]) -> Answer:
    """Read refund windows from supplied evidence, without hidden training data."""
    for item in evidence:
        match = re.search(r"refund window is\s+(\d+)\s+days", item.text, re.I)
        if match:
            return Answer(f"The refund window is {match.group(1)} days.", (item.id,))
    return Answer("I cannot determine the refund period from the available evidence.")

def make_openai_compatible_agent(client, model: str):
    """Inject an OpenAI-compatible SDK client; no package-level API dependency."""
    def agent(question: str, evidence: tuple[Evidence, ...]) -> Answer:
        context = "\n\n".join(f"[{e.id}] {e.text}" for e in evidence)
        prompt = ("Answer only using the provided evidence. If evidence is insufficient, "
                  "say 'I cannot determine from the available evidence'. "
                  "Cite evidence IDs in square brackets.\n\nEvidence:\n"
                  + context + "\n\nQuestion: " + question)
        result = client.chat.completions.create(model=model, messages=[{"role":"user","content":prompt}], temperature=0)
        text = result.choices[0].message.content or ""
        cited = tuple(dict.fromkeys(x for x in re.findall(r"\[([^\]]+)\]", text)))
        return Answer(text, cited)
    return agent
