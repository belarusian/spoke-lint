"""Gate-command extraction and PATH diffing for runner prompts.

Cycle 6 of spoke-lint. A runner prompt typically interleaves *gate* commands
(lint/test/format tools such as ``pytest``, ``ruff``, ``mypy``) with *spoke
invocation* lines (``python .../spokes/foo.py ...``) and free-form prose. The
extractor in :mod:`spoke_lint.extractor` only handles the invocation lines;
this module handles the gate commands.

Two public functions:

- :func:`gate_commands` — extract the leading executable of each gate line,
  in document order.
- :func:`diff_gate_commands` — flag gate executables that are not resolvable
  on ``PATH`` as :class:`~spoke_lint.models.Finding` objects of kind
  ``"missing_tool"``.
"""

from __future__ import annotations

import os
import re
import shutil

from spoke_lint.markdown import iter_lines_outside_code_blocks
from spoke_lint.models import Finding

# A leading run of ``VAR=value`` env-var prefixes, each followed by whitespace.
# Matches the same shape the extractor uses for invocation lines.
_ENV_PREFIX_RE = re.compile(r"(?:\w+=\S+\s+)*")

# A python interpreter token: bare ``python``/``python3`` or an absolute path
# ending in ``/python``/``/python3``.
_PYTHON_INTERP_RE = re.compile(r"^(?:python3?|/\S*/python3?)$")


def _is_python_interpreter(token: str) -> bool:
    """Return True if ``token`` is a python interpreter (a spoke invocation).

    Args:
        token: A single whitespace-separated command token.

    Returns:
        ``True`` when ``token`` is a python interpreter, else ``False``.
    """
    return bool(_PYTHON_INTERP_RE.match(token))


def _is_command_like(tokens: list[str]) -> bool:
    """Return True if ``tokens`` look like a command line rather than prose.

    A gate line is a command, not a sentence. We treat a line as a command when
    it is a single bare token (e.g. ``pytest``) or when it carries at least one
    argument that is a flag (starts with ``-``), a path (contains ``/``), or a
    file name (contains ``.``). Lines made up only of plain words (prose) are
    not commands and are ignored.

    Args:
        tokens: The whitespace-separated tokens of a single line.

    Returns:
        ``True`` when the line looks like a command, else ``False``.
    """
    if len(tokens) == 1:
        return True
    for token in tokens[1:]:
        if token.startswith("-") or "/" in token or "." in token:
            return True
    return False


def gate_commands(text: str) -> list[str]:
    """Return the leading executable of each shell gate line in ``text``.

    A *gate line* is a non-blank, non-comment line whose first command token is
    a bare command name, optionally preceded by ``VAR=value`` env-var prefixes.
    Lines whose first command token is a python interpreter (``python``,
    ``python3``, or an absolute path ending in ``/python``/``/python3``) are
    spoke invocation lines and are NOT gate commands. A line is only treated as
    a gate command when it is command-like (see :func:`_is_command_like`);
    free-form prose is ignored.

    The scan is markdown-aware: lines inside fenced code blocks (and the fence
    delimiter lines themselves) are ignored, so an *illustrative* gate command
    shown in a fenced block does not produce a finding. Only real gate lines
    that appear outside a fenced block are detected.

    Args:
        text: The runner prompt text.

    Returns:
        A list of executable names in document order. Duplicates are preserved;
        no dedup is performed.
    """
    commands: list[str] = []
    for _index, line in iter_lines_outside_code_blocks(text):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        # Strip leading env-var prefixes, if any.
        remainder = _ENV_PREFIX_RE.sub("", stripped)
        if not remainder:
            # Line was only env-var prefixes; no command.
            continue
        tokens = remainder.split()
        first_token = tokens[0]
        if _is_python_interpreter(first_token):
            continue
        if not _is_command_like(tokens):
            continue
        commands.append(first_token)
    return commands


def diff_gate_commands(text: str, path: list[str] | None = None) -> list[Finding]:
    """Flag gate-command executables that are not resolvable on ``path``.

    For each executable from :func:`gate_commands`, resolve it against ``path``
    (defaulting to ``os.environ["PATH"]``) using :func:`shutil.which`. If the
    executable is not found, emit a
    :class:`~spoke_lint.models.Finding` of kind ``"missing_tool"``.

    Args:
        text: The runner prompt text.
        path: An explicit list of directory paths to search. When ``None``,
            the current process ``PATH`` environment variable is used.

    Returns:
        A list of :class:`Finding` in document order (matching the order from
        :func:`gate_commands`). Empty when every gate tool is resolvable.

    This function is pure and deterministic: it performs no I/O beyond the
    ``shutil.which`` lookups and has no side effects.
    """
    if path is None:
        path_str = os.environ.get("PATH", "")
    else:
        path_str = os.pathsep.join(path)
    findings: list[Finding] = []
    for name in gate_commands(text):
        if shutil.which(name, path=path_str) is None:
            findings.append(
                Finding(
                    kind="missing_tool",
                    flag=name,
                    message=f"Gate tool not found on PATH: {name}",
                )
            )
    return findings
