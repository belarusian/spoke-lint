"""Regex extractor for spoke invocation lines in runner prompts.

This is the entry point of the tool: it turns free-form prompt text into a
list of structured :class:`~spoke_lint.models.Invocation` objects, in document
order.
"""

from __future__ import annotations

import re

from spoke_lint.models import Invocation

# Matches a spoke invocation line, anchored at the start of the stripped line.
#   - optional env-var prefixes such as ``FOO=bar `` before the interpreter;
#   - a python interpreter: ``python``, ``python3``, or an absolute path
#     ending in ``/python`` or ``/python3``;
#   - a ``.py`` script path (captured), followed by the remaining tokens.
_INVOCATION_RE = re.compile(
    r"""
    ^
    (?P<env>(?:\w+=\S+\s+)*)             # optional env-var prefixes
    (?P<interp>python3?|/\S*/python3?)   # python interpreter
    \s+
    (?P<script>\S+\.py)                  # script path
    (?P<rest>.*)                         # remaining tokens (args)
    """,
    re.VERBOSE,
)

# A token is a double-quoted string, a single-quoted string, or a run of
# non-whitespace characters. Quoted strings may contain spaces.
_TOKEN_RE = re.compile(r'"[^"]*"|\'[^\']*\'|\S+')


def _tokenize(text: str) -> list[str]:
    """Split ``text`` into tokens, preserving quoted strings as single tokens."""
    return _TOKEN_RE.findall(text)


def _unquote(token: str) -> str:
    """Strip one pair of surrounding single or double quotes, if present."""
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]
    return token


def _is_long_flag(token: str) -> bool:
    """Return True if ``token`` looks like a long flag (``--name``)."""
    return token.startswith("--")


def _parse_args(rest: str) -> list[tuple[str, str | None]]:
    """Parse the tokens after the script path into ordered ``(flag, value)`` pairs.

    A flag consumes the immediately following token as its value unless that
    token is itself a long flag (``--name``), in which case the flag is bare.
    A flag with no following token is bare (``value=None``). Non-flag tokens
    that appear before any flag are ignored (defensive; spokes use only flags).
    """
    tokens = _tokenize(rest)
    args: list[tuple[str, str | None]] = []
    i = 0
    n = len(tokens)
    while i < n:
        token = tokens[i]
        if token.startswith("-"):
            if i + 1 < n and not _is_long_flag(tokens[i + 1]):
                args.append((token, _unquote(tokens[i + 1])))
                i += 2
            else:
                args.append((token, None))
                i += 1
        else:
            # Non-flag token before any flag: ignore (defensive).
            i += 1
    return args


def extract_invocations(text: str) -> list[Invocation]:
    """Extract all spoke invocations from ``text``, in document order.

    A line is an invocation when, after stripping leading whitespace, it starts
    with a python interpreter (optionally preceded by env-var prefixes) followed
    by a ``.py`` script path that contains a ``/spokes/`` segment.
    """
    invocations: list[Invocation] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = _INVOCATION_RE.match(stripped)
        if not match:
            continue
        script = match.group("script")
        if "/spokes/" not in script:
            continue
        args = _parse_args(match.group("rest"))
        invocations.append(Invocation(script_path=script, args=tuple(args)))
    return invocations
