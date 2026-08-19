# TICKET-011 — Multi-option strings + nargs variants in the spoke-signature parser

**Phase:** Signature parsing (Cycle 4)
**Module:** `spoke_lint/parser.py`
**Status:** open

## What
Extend `parse_spoke_args(path) -> list[ArgSpec]` (keep its signature and all existing
rules — positional / store-actions / short-flag / required / default — unchanged and
non-regressing) to handle two more real-world argparse shapes.

### New extraction rules
- **Multiple option strings per arg**: when `add_argument(...)` is given several
  dashed string literals (e.g. `add_argument("-v", "--verbose")`), emit the
  LONG/canonical name — the one with a double leading dash (`--verbose` -> `verbose`).
  If only short options are present (e.g. `-v` alone, or `-a`, `-b`), keep the existing
  behavior (strip dashes; first option wins). A single long option is unchanged.
- **`nargs=` variants**: when a `nargs=` keyword is present with a string-literal value:
  - `"?"` and `"*"` -> the argument is NOT required (`required=False`).
  - `"+"` and an integer (e.g. `2`) -> for a POSITIONAL argument, it IS required
    (`required=True`); for a dashed flag, keep the existing required/default handling.
  The canonical name is still derived from the option-string rules above.

## Why
The diff engine (Cycles 5-7) needs an accurate accepted-argument signature. Real spokes
use short+long aliases and variadic args; without this the parser would emit the wrong
canonical name or misclassify required-ness, producing false diffs.

## Acceptance
- `add_argument("-v", "--verbose")` -> `ArgSpec(name="verbose", ...)`.
- `add_argument("--files", nargs="+")` positional-or-flag keeps canonical name `files`.
- A positional with `nargs="?"` / `nargs="*"` -> `required=False`.
- A positional with `nargs="+"` / `nargs=2` -> `required=True`.
- All existing 55 tests remain green (no regressions).
