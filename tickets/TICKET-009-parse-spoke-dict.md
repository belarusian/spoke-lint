# TICKET-009 — parse_spoke dict lookup helper for the diff engine

**Phase:** Signature parsing (Cycle 3)
**Module:** `spoke_lint/parser.py`
**Status:** open

## What
Add a public helper that returns the spoke's accepted arguments as a name-keyed dict,
for quick lookup by the diff engine (Cycles 5-7).

### Public API
- `parse_spoke(path: str | Path) -> dict[str, ArgSpec]` — parse the spoke at `path`
  and return `{canonical_name: ArgSpec}`.
- **Duplicate names: last one wins** (a later `add_argument` with the same canonical
  name overwrites an earlier entry). Document this in the docstring.
- Raises `FileNotFoundError` for a missing path (same as `parse_spoke_args`).

## Why
The diff engine needs O(1) "does the spoke accept flag X?" lookups rather than
scanning a list each time. A dict keyed by canonical name is the natural shape.

## Acceptance
- `parse_spoke(path)` returns a dict whose values are `ArgSpec` and keys are the
  canonical names (dashes stripped).
- For a spoke with args `--alpha`, `--beta`, `--gamma`: keys == {"alpha","beta","gamma"}.
- A duplicate name (two `add_argument`s with the same flag) keeps the LAST spec.
- Missing file raises `FileNotFoundError`.
