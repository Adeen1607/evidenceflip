"""Command line interface for real, local RAG usage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from .rag import BM25Retriever, OllamaGenerator, RAGPipeline, chunk_sources, evaluate_retrieval, load_sources


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="EvidenceFlip local RAG: ingest, retrieve, generate, evaluate")
    parser.add_argument("--root", default=".", help="Repository root containing sources/manifest.json")
    parser.add_argument("--chunk-size", type=int, default=120)
    parser.add_argument("--overlap", type=int, default=20)
    commands = parser.add_subparsers(dest="command", required=True)
    retrieve = commands.add_parser("retrieve", help="Search verified documents with BM25 (no LLM)")
    retrieve.add_argument("question")
    retrieve.add_argument("--top-k", type=int, default=3)
    ask = commands.add_parser("ask", help="Ask a locally running Ollama model using retrieved sources")
    ask.add_argument("question")
    ask.add_argument("--model", default="llama3.2")
    ask.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    ask.add_argument("--top-k", type=int, default=3)
    benchmark = commands.add_parser("benchmark", help="Measure retrieval on labeled questions")
    benchmark.add_argument("--set", default="examples/retrieval_benchmark.json")
    benchmark.add_argument("--top-k", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        index = BM25Retriever(chunk_sources(load_sources(args.root), args.chunk_size, args.overlap))
        if args.command == "retrieve":
            print(json.dumps([{"source": h.chunk.source_id, "chunk": h.chunk.id,
                               "score": h.score, "text": h.chunk.text}
                              for h in index.search(args.question, args.top_k)], indent=2))
        elif args.command == "ask":
            client = OllamaGenerator(model=args.model, base_url=args.ollama_url)
            response = RAGPipeline(index, client, model=args.model).ask(args.question, args.top_k)
            print(json.dumps(response.to_dict(), indent=2))
        else:
            suite_path = Path(getattr(args, "set"))
            suite = json.loads(suite_path.read_text(encoding="utf-8"))
            result = evaluate_retrieval(RAGPipeline(index, lambda _: "Unused"), suite["queries"], args.top_k)
            print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, RuntimeError) as exc:
        parser.exit(2, f"evidenceflip-rag: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
