# TICKET-014 — Export canonical_names from the package

**Phase:** Signature parsing (Cycle 4)
**Module:** `spoke_lint/__init__.py` (+ `tests/test_package.py`)
**Status:** open

## What
Export the new public helper `canonical_names` from `spoke_lint/__init__.py` alongside
the existing API, and update `tests/test_package.py` so its `__all__` assertion and
import/identity checks include `canonical_names`.

## Acceptance
- `from spoke_lint import canonical_names` works.
- `spoke_lint.__all__` includes `"canonical_names"`.
- `test_package.py` passes; no regressions.
