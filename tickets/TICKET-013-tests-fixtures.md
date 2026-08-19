# TICKET-013 — Tests + fixtures for multi-option, nargs, subparsers, canonical_names

**Phase:** Signature parsing (Cycle 4)
**Module:** `tests/test_parser.py` (+ original fixtures under `tests/fixtures/`)
**Status:** open

## What
Deterministic tests for the new Cycle 4 parser behavior using small ORIGINAL fixture
spoke scripts under `tests/fixtures/` (do NOT copy seed files). Keep all existing tests
green.

### New fixtures (original)
- multi-option-string spoke: `add_argument("-v", "--verbose")`.
- nargs spoke: a positional with `nargs="+"`, one with `nargs="?"`, and a dashed flag
  with `nargs="*"`.
- subparser spoke: an `ArgumentParser` with `add_subparsers()` and two `add_parser(...)`
  subcommands, each with its own `add_argument(...)`.

### Test cases
- Multi-option -> canonical LONG name (`verbose`, not `v`).
- Each `nargs` variant's required-ness (positional `?`/`*` not required; `+`/int required).
- Subparser args collected with correct prefix-free names.
- `canonical_names` helper (set of names, empty case).
- No regressions to the 55 existing passing tests.

## Acceptance
- All tests pass under `pytest tests/ -x -q`.
