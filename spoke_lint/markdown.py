"""Markdown-aware line scanning: skip fenced code blocks.

Cycle 14 of spoke-lint. A runner prompt or log frequently contains *illustrative*
fenced markdown code blocks: a block showing example JSON output, a block quoting
the 6-phase runner prompt's command examples, or a block showing a non-spoke
python snippet. Those lines must NOT be treated as real tool calls (gate commands
or spoke invocations). This module provides a single, shared helper that yields
only the lines that appear OUTSIDE fenced code blocks, so both
:mod:`spoke_lint.extractor` and :mod:`spoke_lint.gate` can be made
markdown-aware without duplicating the fence-tracking logic.

Fence semantics
---------------
A line whose **stripped** form starts with three backticks (optionally followed
by a language tag, e.g. a python tag), toggles the in/out-of-code-block state.
While inside a fenced code block -- including the fence delimiter lines
themselves -- a line is not yielded. An unclosed fence (an opening fence with no
closing fence) causes every line after the opening fence to be ignored. A fenced
block with a language tag is handled exactly the same as a bare fence.
"""

from __future__ import annotations

from collections.abc import Iterator

# The minimum number of backticks that mark a fence delimiter.
_FENCE_PREFIX = "```"


def _is_fence(line: str) -> bool:
    """Return True if ``line`` is a fenced-code-block delimiter.

    A delimiter is a line whose stripped form starts with three backticks,
    optionally followed by a language tag (e.g. a python tag).

    Args:
        line: A single line of text.

    Returns:
        ``True`` when ``line`` is a fence delimiter, else ``False``.
    """
    return line.strip().startswith(_FENCE_PREFIX)


def iter_lines_outside_code_blocks(text: str) -> Iterator[tuple[int, str]]:
    """Yield the lines of ``text`` that are OUTSIDE fenced code blocks.

    Each yielded item is a ``(index, line)`` pair where ``index`` is the line's
    original 0-based position in ``text`` and ``line`` is the line's text (with
    its original leading/trailing whitespace preserved). Lines inside a fenced
    code block -- and the fence delimiter lines themselves -- are never yielded.

    Args:
        text: The full text to scan (typically a runner prompt or log).

    Yields:
        ``(index, line)`` for every line that is not inside a fenced code block,
        in document order.

    This function is pure and deterministic: it performs no I/O and has no side
    effects.
    """
    in_block = False
    for index, line in enumerate(text.splitlines()):
        if _is_fence(line):
            # A fence delimiter toggles the state and is itself skipped.
            in_block = not in_block
            continue
        if in_block:
            # Inside a fenced code block: skip the line.
            continue
        yield index, line
