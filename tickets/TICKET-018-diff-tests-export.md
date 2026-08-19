# TICKET-018 — diff tests + package export

**Phase:** Diffing (Cycle 5)
**Module:** `tests/test_diff.py`, `spoke_lint/__init__.py`
**Status:** open

## What
- Add `tests/test_diff.py` with deterministic tests using the existing fixtures plus
  small in-repo prompt strings:
  - unknown flag detected;
  - missing required arg detected;
  - a fully-valid invocation yields no findings;
  - multiple invocations aggregate in order;
  - a non-existent referenced script yields a `missing_script` finding (not an exception).
- Export the new public API from `spoke_lint/__init__.py`: `diff_invocation`,
  `diff_prompt`, and `Finding`. Update `tests/test_package.py` for the new `__all__`.

## Why
Every module must be tested before merge, and the package surface must expose the diff
engine so later cycles (reporting/CLI) can import it.

## Acceptance
- All new tests pass; all 71 existing tests remain green (no regressions).
- `spoke_lint.__all__` includes `diff_invocation`, `diff_prompt`, `Finding`.
- Gate passes: pytest + ruff + mypy.
