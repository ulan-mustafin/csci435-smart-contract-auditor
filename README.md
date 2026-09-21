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
Run `pip install -e .`.
Set `OPENAI_API_KEY`.
