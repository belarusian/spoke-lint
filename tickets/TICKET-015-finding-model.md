# TICKET-015 — Finding value object for the diff engine

**Phase:** Diffing (Cycle 5)
**Module:** `spoke_lint/models.py`
**Status:** open

## What
Add a frozen, hashable dataclass `Finding(kind: str, flag: str, message: str)` to
`spoke_lint/models.py`, alongside the existing `Invocation` and `ArgSpec`.

- `kind`: a stable enum-like string identifying the finding category. Cycle 5 uses
  `"unknown_flag"`, `"missing_required"`, and `"missing_script"`.
- `flag`: the argument name (canonical, dashes stripped) the finding is about; for
  `missing_script` this is the referenced script path.
- `message`: a human-readable one-line description.

Keep it stdlib-only (`dataclasses`), frozen, and hashable/comparable so later cycles
can render a deterministic report and tests can assert on exact instances.

## Why
The diff engine (this ticket + TICKET-016) needs a single structured result type that
is stable across runs and easy to aggregate, sort, and render.

## Acceptance
- `Finding` is frozen (assignment raises `FrozenInstanceError`).
- `Finding` is hashable; equal instances hash equal.
- All three fields are present with the documented defaults/semantics.
