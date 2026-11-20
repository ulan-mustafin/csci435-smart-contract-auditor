import argparse
from collections.abc import Sequence
from pathlib import Path
import sys
from urllib.error import URLError

from smart_contract_auditor.benchmark import run_benchmark
from smart_contract_auditor.cache import CachedClient
from smart_contract_auditor.dataset import load_dataset
from smart_contract_auditor.llm_client import GeminiClient, LLMClient, OpenRouterClient, load_env_file
from smart_contract_auditor.prompts import build_prompt, load_prompt

PROVIDERS = ("gemini", "openrouter")


def create_client(provider: str, model: str) -> LLMClient:
    if provider == "openrouter":
        return OpenRouterClient(model=model)
    return GeminiClient(model=model)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="smart-contract-auditor")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--labels", type=Path, default=Path("data/raw/labels.json"))
    parser.add_argument("--prompts-dir", type=Path, default=Path("prompts"))
    parser.add_argument("--prompt", default="vulnerability_audit")
    parser.add_argument("--output", type=Path, default=Path("reports"))
    parser.add_argument("--model", required=True)
    parser.add_argument("--provider", choices=PROVIDERS, default="gemini")
    parser.add_argument("--responses", type=Path, default=Path("results/raw/responses.jsonl"))
    parser.add_argument("--run", type=int, default=1)
    parser.add_argument("--offline", action="store_true", help="use only stored responses")
    args = parser.parse_args(argv)

    try:
        root = args.root.resolve()
        samples = load_dataset(root / args.labels, root)
        if not samples:
            raise ValueError("Dataset is empty")
        template = load_prompt(args.prompt, root / args.prompts_dir)
        build_prompt(template, "")
        client = None
        if not args.offline:
            load_env_file(root / ".env")
            client = create_client(args.provider, args.model)
        client = CachedClient(root / args.responses, f"{args.provider}:{args.model}", client, args.run)
        run_benchmark(samples, template, client, root / args.output)
    except (OSError, ValueError, RuntimeError, URLError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0
