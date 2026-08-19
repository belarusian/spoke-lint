# TICKET-002 — Regex extractor for spoke invocation lines

**Phase:** Extraction (Cycle 1)
**Module:** `spoke_lint/extractor.py`
**Status:** open

## What
Find every spoke invocation line in a runner prompt and parse it into an `Invocation`.

### Public API
- `extract_invocations(text: str) -> list[Invocation]` — scan all lines, return one `Invocation` per matching line, in document order.
- A line matches when it (after stripping leading whitespace/indentation) starts with a python interpreter (`python`, `python3`, or an absolute path ending in `/python3`) followed by a `.py` script path that contains a `/spokes/` segment.

### Parsing rules
- The script path is the first token after the interpreter that ends in `.py`.
- Remaining tokens are parsed into ordered `(flag, value)` pairs:
  - A token starting with `-` (one or two dashes) is a flag.
  - If the next token does NOT start with `-`, it is the flag's value; otherwise the flag is bare (`value=None`).
  - Non-flag tokens that appear before any flag are ignored (defensive; spokes use only flags).
- Env-var prefixes like `FIVE_MODEL=x python ...` must still be detected (interpreter may not be the first token).

## Why
This is the entry point of the whole tool: it turns free-form prompt text into structured invocations.

## Acceptance
- Detects `python3 ~/.../spokes/essay-pipeline.py --topic "X" --endpoint http://...` → script_path + `[("--topic","X"), ("--endpoint","http://...")]`.
- Handles 4-space indentation, `python` (no 3), and env-var prefixes.
- Bare flags (`--verbose`) yield `value=None`.
- Non-invocation lines (prose, other commands) are ignored.
