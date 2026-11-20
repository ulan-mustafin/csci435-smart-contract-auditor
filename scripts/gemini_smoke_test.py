"""Send sample contracts to Gemini and print its answers.

Usage (from the repository root):
    python scripts/gemini_smoke_test.py [CONTRACT.sol ...] [--model MODEL] [--prompt NAME]

The API key is read from GEMINI_API_KEY, or from the .env file in the
repository root.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from smart_contract_auditor.llm_client import GeminiClient, load_env_file  # noqa: E402
from smart_contract_auditor.prompts import build_prompt, load_prompt  # noqa: E402

DEFAULT_CONTRACTS = [
    ROOT / "contracts" / "reentrancy_vulnerable.sol",
    ROOT / "contracts" / "integer_overflow_vulnerable.sol",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Send contracts to Gemini and print its answers.")
    parser.add_argument("contracts", nargs="*", type=Path, default=DEFAULT_CONTRACTS)
    parser.add_argument("--model", default="gemini-3.8-flash")
    parser.add_argument("--prompt", default="definitions_audit")
    args = parser.parse_args()

    load_env_file(ROOT / ".env")
    client = GeminiClient(model=args.model)
    template = load_prompt(args.prompt, ROOT / "prompts")

    for contract in args.contracts:
        answer = client.ask(build_prompt(template, contract.read_text(encoding="utf-8")))
        try:
            answer = json.dumps(json.loads(answer), indent=2)
        except json.JSONDecodeError:
            pass
        print(f"=== {contract.name} ({args.model}) ===")
        print(answer)
        print()


if __name__ == "__main__":
    main()
