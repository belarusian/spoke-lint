# TICKET-005 — AST-based spoke-signature parser

**Phase:** Extraction -> Signature parsing boundary (Cycle 2)
**Module:** `spoke_lint/parser.py`
**Status:** open

## What
Parse a spoke script's argparse signature into a list of `ArgSpec` value objects,
consuming the dataclasses established in Cycle 1.

### Public API
- `parse_spoke_args(path: str | Path) -> list[ArgSpec]` — read the file at `path`,
  parse it with `ast`, walk the tree for `argparse.ArgumentParser.add_argument(...)`
  calls, and return one `ArgSpec` per argument in source order.

### Extraction rules
- Locate every call whose callee is an attribute `add_argument` on a variable that was
  bound to `argparse.ArgumentParser(...)` (track the binding, then match `.add_argument`).
- For each such call:
  - **name**: the first positional string-literal argument, with leading dashes
    stripped (canonical name). If the first positional is not a string literal, skip.
  - **required**: `True` iff a `required=True` keyword is present; else `False`.
  - **default**: the stringified value of a `default=` keyword if present
    (`ast.literal_eval` when it is a literal); `None` (no explicit default) otherwise.
- Handle multi-line `add_argument(...)` calls, `type=...`, `default=None`,
  `required=True`, and multiple args in order.

## Why
This is the second half of the extraction layer: it turns a referenced spoke script
into its accepted-argument signature, which the diff engine (Cycles 5-7) compares
against the invocations extracted from the runner prompt.

## Acceptance
- `parser.add_argument("--topic", required=True)` -> `ArgSpec(name="topic", required=True, default=None)`.
- `parser.add_argument("--max-steps", type=int, default=150)` -> `ArgSpec(name="max-steps", required=False, default="150")` (name is the flag text minus leading dashes; `type=` is ignored).
- `parser.add_argument("--briefing", default=None)` -> `ArgSpec(name="briefing", required=False, default=None)`.
- Multi-line call with trailing comma parses identically to single-line.
- A script with no `add_argument` calls returns `[]`.
