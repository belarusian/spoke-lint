# TICKET-034 — README + package export consistency for the `check` subcommand

**Cycle:** 9 (CLI phase, Build Order phase 7)
**Module:** `README.md`, `spoke_lint/__init__.py`, `tests/test_package.py`

## Capability
Ensure the documented CLI usage matches the implemented subcommand exactly, and keep
the public API surface deliberate.

### README.md
- The documented invocation `spoke-lint check <runner-prompt> --spokes-dir <dir>`
  must match the implemented `check` subcommand (it already does; verify and, if
  useful, note the optional `--path` flag). Do not introduce drift.

### spoke_lint/__init__.py / tests/test_package.py
- No new exports are required for this refactor (`build_parser`, `run` are already
  exported). If `__all__` changes, update `tests/test_package.py` accordingly and keep
  the change deliberate. Otherwise leave the export set unchanged.

## Rules
- stdlib-only; no behavior change beyond the CLI subcommand refactor.
- Do not regress the 144 passing tests from Cycle 8.

## Acceptance
- README usage matches `spoke-lint check <prompt> --spokes-dir <dir>` (and optional
  `--path`).
- `tests/test_package.py` still green; `__all__` unchanged unless deliberately changed.
