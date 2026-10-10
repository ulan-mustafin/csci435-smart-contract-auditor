"""Prepare contract source code before it is sent to the LLM."""


def clean_source(source_code: str) -> str:
    """Remove ``//`` and ``/* */`` comments from Solidity source code.

    Benchmark files often contain hints such as ``@vulnerable_at_lines`` or
    ``// <yes> <report> REENTRANCY`` that would give the answer away.
    """
    raise NotImplementedError
