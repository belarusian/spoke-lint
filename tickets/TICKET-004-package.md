# TICKET-004 — Package exports + gate green

**Phase:** Extraction (Cycle 1)
**Module:** `spoke_lint/__init__.py`
**Status:** open

## What
Expose the public API from the package root and keep the gate green.

### Public API in `spoke_lint/__init__.py`
- Re-export `Invocation`, `ArgSpec` (from `.models`) and `extract_invocations` (from `.extractor`).
- Define `__all__ = ["Invocation", "ArgSpec", "extract_invocations"]`.
- Add a short module docstring.

## Why
Downstream phases (parser, diff, cli) import from the package root; keep the surface stable and explicit.

## Acceptance
- `from spoke_lint import Invocation, ArgSpec, extract_invocations` works.
- Gate green: `pytest tests/ -x -q`, `ruff check spoke_lint/`, `mypy spoke_lint/ --ignore-missing-imports`.
