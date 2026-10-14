"""Prepare contract source code before it is sent to the LLM."""

import re


_COMMENT_OR_STRING = re.compile(
    r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|//[^\n]*|/\*[\s\S]*?\*/'
)


def clean_source(source_code: str) -> str:
    """Remove ``//`` and ``/* */`` comments from Solidity source code.

    Benchmark files often contain hints such as ``@vulnerable_at_lines`` or
    ``// <yes> <report> REENTRANCY`` that would give the answer away.
    """
    def remove_comment(match: re.Match[str]) -> str:
        text = match.group()
        if text.startswith(('"', "'")):
            return text
        return "".join("\n" if character == "\n" else " " for character in text)

    return _COMMENT_OR_STRING.sub(remove_comment, source_code)
