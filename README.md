# Smart Contract Auditor
This project uses an LLM to audit Solidity contracts.
It checks for reentrancy and integer overflow.
It compares findings with labeled contracts.
It reports precision and recall.

## Layout
- `src/` contains the auditor.
- `contracts/` contains Solidity inputs.
- `data/` contains labels and processed data.
- `prompts/` contains LLM prompts.
- `reports/` contains benchmark results.
- `tests/` contains tests.

## Setup
Requires Python 3.11 or newer. From a clean clone, run:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest -q
```

On Windows, activate with `.venv\Scripts\activate` instead.

The unit tests use a fake LLM client and do not need an API key. The labeled
benchmark inputs are `data/raw/labels.json` and the Solidity files in
`contracts/`. `prompts/vulnerability_audit.txt` defines the audit instructions.
For a live Gemini call, set `GEMINI_API_KEY` in your environment; do not commit
keys. The complete benchmark runner and report generation are not yet implemented.
