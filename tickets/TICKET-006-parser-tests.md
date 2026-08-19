# TICKET-006 — Deterministic tests for the spoke-signature parser

**Phase:** Extraction -> Signature parsing boundary (Cycle 2)
**Module:** `tests/test_parser.py` (+ original fixtures under `tests/fixtures/`)
**Status:** open

## What
Deterministic unit tests for `parse_spoke_args`, using small ORIGINAL fixture spoke
scripts written under `tests/fixtures/` (do NOT copy seed files).

### Fixture coverage (one or more scripts)
- required flag: `--topic` with `required=True`.
- default int: `--max-steps` with `type=int, default=150`.
- default None: `--briefing` with `default=None`.
- multi-line `add_argument(...)` call (trailing comma, wrapped lines).
- multiple args in a single parser, verifying source order is preserved.
- no-arg script: a spoke with an ArgumentParser but zero add_argument calls -> `[]`.

### Test cases
- Each fixture yields the expected list of `ArgSpec` (name/required/default).
- Order preservation across multiple args.
- `default=None` vs absent default both map to `default=None`.
- `type=` is ignored (only name/required/default are surfaced).
- Missing file raises a clear error (e.g. `FileNotFoundError`).

## Acceptance
- All tests pass under `pytest tests/ -x -q`.
- Fixtures are self-contained, original, and live in `tests/fixtures/`.
