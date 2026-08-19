# TICKET-010 — Tests + fixtures for robust parser shapes and parse_spoke

**Phase:** Signature parsing (Cycle 3)
**Module:** `tests/test_parser.py` (+ original fixtures under `tests/fixtures/`)
**Status:** open

## What
Deterministic tests for the new parser behavior, using small ORIGINAL fixture spoke
scripts written under `tests/fixtures/` (do NOT copy seed files). Keep all existing
Cycle 2 tests green.

### New fixtures (original)
- positional-only spoke: a single `add_argument("topic")` positional.
- short-flag spoke: `-v` short flag.
- store-action spoke: `--verbose` with `action="store_true"`, plus a `count` action arg.

### Test cases
- Positional arg -> `ArgSpec(name=<name>, required=True, default=None)`.
- Short flag `-v` -> name `v`, required False, default None.
- `store_true` / `store_false` / `count` actions -> required False, default None.
- `parse_spoke` returns a dict keyed by canonical name with `ArgSpec` values.
- `parse_spoke` last-wins on duplicate names.
- `parse_spoke` missing file raises `FileNotFoundError`.

## Acceptance
- All tests pass under `pytest tests/ -x -q`.
- No regressions to the 45 existing passing tests.
