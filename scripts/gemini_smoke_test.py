"""Send sample contracts to Gemini and print its answers.

Usage (from the repository root):
    python scripts/gemini_smoke_test.py [CONTRACT.sol ...] [--model MODEL]

The API key is read from GEMINI_API_KEY, or from the .env file in the
repository root.
"""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from smart_contract_auditor.llm_client import GeminiClient  # noqa: E402

DEFAULT_CONTRACTS = [
    ROOT / "contracts" / "reentrancy_vulnerable.sol",
    ROOT / "contracts" / "integer_overflow_vulnerable.sol",
]

PROMPT = """You are a smart contract security auditor.
Check the Solidity contract below for these vulnerability types only:
- reentrancy
- integer_overflow (includes underflow; Solidity >= 0.8.0 reverts on overflow
  automatically, except inside `unchecked { }` blocks)

Respond with JSON only, in this format:
{"vulnerabilities": [{"type": "reentrancy" | "integer_overflow", "function": "<name>", "reason": "<one sentence>"}]}
If the contract has neither vulnerability, return {"vulnerabilities": []}.

Contract:
"""


def load_env_file(path: Path) -> None:
    """Copy KEY=VALUE lines from ``path`` into the environment (existing values win)."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Send contracts to Gemini and print its answers.")
    parser.add_argument("contracts", nargs="*", type=Path, default=DEFAULT_CONTRACTS)
    parser.add_argument("--model", default="gemini-3.8-flash")
    args = parser.parse_args()

    load_env_file(ROOT / ".env")
    client = GeminiClient(model=args.model)

    for contract in args.contracts:
        answer = client.ask(PROMPT + contract.read_text(encoding="utf-8"))
        try:
            answer = json.dumps(json.loads(answer), indent=2)
        except json.JSONDecodeError:
            pass
        print(f"=== {contract.name} ({args.model}) ===")
        print(answer)
        print()


if __name__ == "__main__":
    main()
