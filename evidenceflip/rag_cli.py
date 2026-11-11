"""Command line interface for real, local RAG usage."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import time

from .dense import DEFAULT_EMBEDDING_MODEL, DenseRetriever, SentenceTransformerEncoder
from .rag import BM25Retriever, OllamaGenerator, RAGPipeline, chunk_sources, evaluate_retrieval, load_sources
from .ingest import register_source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="EvidenceFlip local RAG: ingest, retrieve, generate, evaluate")
    parser.add_argument("--root", default=".", help="Repository root containing sources/manifest.json")
    parser.add_argument("--chunk-size", type=int, default=120)
    parser.add_argument("--overlap", type=int, default=20)
    parser.add_argument("--retriever", choices=("bm25", "dense"), default="bm25",
                        help="BM25 needs no model; dense needs the optional sentence-transformers extra")
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL,
                        help="Sentence-transformers model ID used only with --retriever dense")
    commands = parser.add_subparsers(dest="command", required=True)
    register = commands.add_parser("register", help="Import a permitted Markdown or text document into the source registry")
    register.add_argument("--file", required=True)
    register.add_argument("--id", required=True)
    register.add_argument("--title", required=True)
    register.add_argument("--origin", required=True)
    register.add_argument("--license", required=True)
    retrieve = commands.add_parser("retrieve", help="Search verified documents (no LLM)")
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
        if args.command == "register":
            entry = register_source(args.root, args.file, args.id, title=args.title,
                                    origin=args.origin, license=args.license)
            print(json.dumps(entry, indent=2))
            return 0
        chunks = chunk_sources(load_sources(args.root), args.chunk_size, args.overlap)
        if args.retriever == "dense":
            index = DenseRetriever(chunks, SentenceTransformerEncoder(args.embedding_model))
        else:
            index = BM25Retriever(chunks)
        if args.command == "retrieve":
            print(json.dumps([{"source": h.chunk.source_id, "chunk": h.chunk.id,
                               "score": h.score, "text": h.chunk.text,
                               "source_path": h.chunk.source_path,
                               "source_sha256": h.chunk.source_sha256,
                               "source_license": h.chunk.source_license}
                              for h in index.search(args.question, args.top_k)], indent=2))
        elif args.command == "ask":
            client = OllamaGenerator(model=args.model, base_url=args.ollama_url)
            response = RAGPipeline(index, client, model=args.model).ask(args.question, args.top_k)
            print(json.dumps(response.to_dict(), indent=2))
        else:
            suite_path = Path(args.set)
            if not suite_path.is_absolute():
                suite_path = Path(args.root) / suite_path
            suite_bytes = suite_path.read_bytes()
            suite = json.loads(suite_bytes.decode("utf-8"))
            start = time.perf_counter()
            result = evaluate_retrieval(RAGPipeline(index, lambda _: "Unused"), suite["queries"], args.top_k)
            result["retrieval_elapsed_ms"] = round((time.perf_counter() - start) * 1000, 2)
            result["configuration"] = {
                "retriever": args.retriever,
                "embedding_model": args.embedding_model if args.retriever == "dense" else None,
                "chunk_size_words": args.chunk_size,
                "overlap_words": args.overlap,
                "source_manifest_sha256": hashlib.sha256(
                    (Path(args.root) / "sources/manifest.json").read_bytes()).hexdigest(),
                "benchmark_sha256": hashlib.sha256(suite_bytes).hexdigest(),
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "random_seed": None,
            }
            print(json.dumps(result, indent=2))
    except (ValueError, OSError, KeyError, RuntimeError) as exc:
        parser.exit(2, f"evidenceflip-rag: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
