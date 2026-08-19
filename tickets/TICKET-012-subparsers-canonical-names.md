# TICKET-012 — Subparser collection + canonical_names helper

**Phase:** Signature parsing (Cycle 4)
**Module:** `spoke_lint/parser.py`
**Status:** open

## What
Two additions to `spoke_lint/parser.py`:

### 1. Subparser support in `parse_spoke_args`
Collect arguments from sub-parsers too, so a spoke that dispatches on a command still
exposes its flags:
- Track the return value of `add_subparsers(...)` (the subparser action object) and any
  variable bound to it.
- For each `add_parser("cmd", ...)` call on that object, track the returned sub-parser
  name; then collect `.add_argument(...)` calls on those sub-parsers.
- Sub-parser args are emitted with their prefix-free canonical names (dashes stripped),
  in source order, interleaved with top-level args by line number.

### 2. `canonical_names(specs: list[ArgSpec]) -> set[str]`
A small pure helper the diff engine will reuse for O(1) membership checks: returns the
set of canonical accepted names derived from the same extraction rules (i.e.
`{spec.name for spec in specs}`). Document that it is derived from the same rules as
`parse_spoke_args`.

## Why
Command-dispatch spokes are common; dropping their per-subcommand flags would make the
diff engine report every subcommand flag as "not accepted". `canonical_names` gives the
diff engine a cheap membership set.

## Acceptance
- A spoke with `add_subparsers()` + two `add_parser(...)` each with an `add_argument`
  yields all three (or more) args with correct canonical names.
- `canonical_names([ArgSpec("a"), ArgSpec("b")]) == {"a", "b"}`; empty list -> empty set.
- All existing 55 tests remain green (no regressions).
