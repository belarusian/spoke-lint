# TICKET-007 — Export parse_spoke_args from the package

**Phase:** Extraction -> Signature parsing boundary (Cycle 2)
**Module:** `spoke_lint/__init__.py` (+ update `tests/test_package.py`)
**Status:** open

## What
Add `parse_spoke_args` to the public API.

### Changes
- Import `parse_spoke_args` from `spoke_lint.parser`.
- Add it to `__all__` (keep existing entries; order: Invocation, ArgSpec,
  extract_invocations, parse_spoke_args).
- Update `tests/test_package.py` so the public-API assertions include
  `parse_spoke_args` and the exact `__all__` list.

## Acceptance
- `from spoke_lint import parse_spoke_args` works.
- `spoke_lint.__all__ == ["Invocation", "ArgSpec", "extract_invocations", "parse_spoke_args"]`.
