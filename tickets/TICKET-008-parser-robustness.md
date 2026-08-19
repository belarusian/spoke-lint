# TICKET-008 — Robust argparse shapes in the spoke-signature parser

**Phase:** Signature parsing (Cycle 3)
**Module:** `spoke_lint/parser.py`
**Status:** open

## What
Extend `parse_spoke_args(path) -> list[ArgSpec]` (keep its signature and existing
required/default/type behavior unchanged) so it is robust to the real-world argparse
shapes that appear in spoke scripts.

### New extraction rules (in addition to the existing dashed-flag handling)
- **Positional arguments**: when the first positional string literal has NO leading
  dash, treat it as a positional argument and emit
  `ArgSpec(name=<name>, required=True, default=None)` regardless of any other keywords.
- **Short flags**: `-v` (single leading dash) is handled by the existing
  "strip leading dashes" rule and yields canonical name `v`. No special-casing needed;
  just confirm it works.
- **Store-type actions**: when an `action=` keyword is present with a string-literal
  value in `{"store_true", "store_false", "count"}`, the argument is a boolean/count
  flag that takes no value — surface it as `required=False, default=None` (ignore any
  `default=`/`type=` keywords for these).

### Out of scope
- A parser bound via `argparse.ArgumentParser(...)` assigned to a tuple of names is
  out of scope (only single-name `Assign` targets are tracked, as today).

## Why
The diff engine (Cycles 5-7) compares prompt invocations against the spoke's accepted
signature. Positional args and boolean/count flags are common in real spokes; without
this the parser would misclassify or drop them.

## Acceptance
- `parser.add_argument("topic")` -> `ArgSpec(name="topic", required=True, default=None)`.
- `parser.add_argument("-v")` -> `ArgSpec(name="v", required=False, default=None)`.
- `parser.add_argument("--verbose", action="store_true")` -> `ArgSpec(name="verbose", required=False, default=None)`.
- `parser.add_argument("--count", action="count")` -> `ArgSpec(name="count", required=False, default=None)`.
- Existing dashed-flag / multi-line / type / default behavior is unchanged (no regressions).
