"""Input-contract detection for spoke-lint.

spoke-lint's input contract is a **runner prompt**: free-form markdown prose
that may embed fenced bash blocks (gate commands, spoke invocations). A pure
shell launch script (a shebang, ``set``/``export``/``trap`` statements,
heredocs, ``VAR=value`` assignments) is *not* a valid input. Linting one used
to flood the report with a ``missing_tool`` finding for the first token of
every shell line (``set``, ``export``, ``<<'EOF'``, ``Mission:``, ``)`` ...),
burying any real finding.

This module provides a single, pure, deterministic predicate —
:func:`is_runner_prompt` — that the CLI uses to reject non-runner-prompt input
with a clean exit-2 diagnostic instead of a false-positive flood.

Detection operates on the lines **outside** fenced code blocks (via
:func:`spoke_lint.markdown.iter_lines_outside_code_blocks`): in a real runner
prompt the shell commands live *inside* fenced blocks and are ignored, so the
outside-block content is markdown prose. In a pure shell script there are no
fenced blocks, so the shell statements are all "outside" and are detected.
"""

from __future__ import annotations

import re

from spoke_lint.markdown import iter_lines_outside_code_blocks

# A shebang line (``#!/bin/bash``) is unambiguously a shell script, never a
# runner prompt.
_SHEBANG_RE = re.compile(r"^#!")

# A heredoc marker (``<<`` / ``<<'EOF'`` / ``<<-EOF``) is unambiguously shell.
_HEREDOC_RE = re.compile(r"<<")

# Shell statements that are strong, unambiguous signals of a shell script when
# they lead a line (outside any fenced block). Prose in a runner prompt does not
# take these forms: ``set`` requires a leading dash flag, ``export`` requires a
# ``VAR=`` assignment, ``trap`` is a shell builtin, and a bare ``VAR=`` line is
# an assignment, not a sentence.
_EXPORT_RE = re.compile(r"^\s*export\s+[A-Za-z_]\w*=")
_SET_FLAG_RE = re.compile(r"^\s*set\s+-")
_TRAP_RE = re.compile(r"^\s*trap\s+")
_ASSIGN_RE = re.compile(r"^\s*[A-Za-z_]\w*=")


def is_runner_prompt(text: str) -> bool:
    """Return ``True`` when ``text`` looks like a runner prompt.

    A runner prompt is markdown prose (optionally with fenced bash blocks). A
    pure shell launch script is rejected. The decision is made on the lines
    outside fenced code blocks:

    - a shebang line anywhere outside a block → not a runner prompt;
    - a heredoc marker (``<<``) anywhere outside a block → not a runner prompt;
    - otherwise, two or more shell-statement lines (``export VAR=``,
      ``set -…``, ``trap …``, or a bare ``VAR=`` assignment) outside a block →
      not a runner prompt.

    Everything else is treated as a runner prompt (the lint proceeds normally).

    Args:
        text: The input text to classify.

    Returns:
        ``True`` when the input is a runner prompt, ``False`` when it is a pure
        shell / non-runner-prompt input. Pure and deterministic: no I/O, no side
        effects.
    """
    shell_statement_count = 0
    for _index, line in iter_lines_outside_code_blocks(text):
        stripped = line.strip()
        if not stripped:
            continue
        if _SHEBANG_RE.match(stripped):
            return False
        if _HEREDOC_RE.search(stripped):
            return False
        if (
            _EXPORT_RE.match(stripped)
            or _SET_FLAG_RE.match(stripped)
            or _TRAP_RE.match(stripped)
            or _ASSIGN_RE.match(stripped)
        ):
            shell_statement_count += 1
            if shell_statement_count >= 2:
                return False
    return True
