"""Command line interface: python -m evidenceflip verify|demo|evaluate."""
import argparse
import json
from pathlib import Path
from .core import Evidence, Scenario, evaluate, verify_registry, compare, to_dict
from .agents import policy_agent

def load_scenarios(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [Scenario(
        name=s["name"], question=s["question"],
        evidence=tuple(Evidence(e["id"], e["text"]) for e in s["evidence"]),
        expected_text=s.get("expected_text"),
        expected_citations=tuple(s["expected_citations"]) if "expected_citations" in s else None,
        expect_abstention=s.get("expect_abstention", False),
    ) for s in data["scenarios"]]

def main(argv=None):
    parser = argparse.ArgumentParser(prog="evidenceflip", description="DATA INTEGRITY evaluation for evidence-grounded AI")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("verify", help="Verify registered source hashes")
    v.add_argument("--root", default=".")
    e = sub.add_parser("evaluate", help="Run JSON scenario suite with reference adapter")
    e.add_argument("suite")
    e.add_argument("--output", default=None)
    e.add_argument("--ollama-model", default=None, help="Use a real local Ollama model instead of the deterministic demo adapter")
    e.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    e.add_argument("--top-k", type=int, default=3)
    d = sub.add_parser("demo", help="Run included evaluation suite")
    d.add_argument("--output", default=None)
    args = parser.parse_args(argv)
    if args.command == "verify":
        results = verify_registry(args.root)
        print(json.dumps(results, indent=2))
        return 0 if all(r["valid"] for r in results) else 1
    suite = args.suite if args.command == "evaluate" else str(Path(__file__).resolve().parent.parent / "examples" / "refund_scenarios.json")
    agent = policy_agent
    if args.command == "evaluate" and args.ollama_model:
        from .rag import OllamaGenerator
        from .rag_adapter import make_rag_agent
        agent = make_rag_agent(OllamaGenerator(model=args.ollama_model, base_url=args.ollama_url), top_k=args.top_k)
    results = [evaluate(s, agent) for s in load_scenarios(suite)]
    payload = {"summary": {"total": len(results), "passed": sum(r.passed for r in results)}, "results": [to_dict(r) for r in results]}
    content = json.dumps(payload, indent=2)
    if args.output:
        Path(args.output).write_text(content + "\n", encoding="utf-8")
    print(content)
    return 0 if all(r.passed for r in results) else 1

if __name__ == "__main__":
    raise SystemExit(main())
