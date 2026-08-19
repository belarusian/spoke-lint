# TICKET-016 — diff_invocation: compare one invocation against a signature

**Phase:** Diffing (Cycle 5)
**Module:** `spoke_lint/diff.py`
**Status:** open

## What
Create `spoke_lint/diff.py` with
`diff_invocation(invocation: Invocation, specs: list[ArgSpec]) -> list[Finding]`.

For one invocation of a spoke, compare the flags actually passed
(`invocation.flag_names()`) against the accepted signature (`specs`):

- **(a) unknown flag** — a passed flag whose canonical name is NOT in
  `canonical_names(specs)` -> emit `Finding("unknown_flag", <name>, ...)`.
- **(b) missing required arg** — an accepted spec with `required=True` whose name was
  not among the passed flags -> emit `Finding("missing_required", <name>, ...)`.

Use `canonical_names(specs)` for O(1) membership. Findings must be deterministic:
unknown-flag findings in invocation order, then missing-required findings in signature
order (document this ordering).

## Why
This is the core comparison primitive the top-level entry point (TICKET-017) reuses per
invocation. It isolates the "what's wrong with one call" logic for focused testing.

## Acceptance
- A fully-valid invocation yields `[]`.
- An unknown flag yields exactly one `unknown_flag` finding naming that flag.
- A missing required arg yields a `missing_required` finding naming that spec.
- Ordering is stable and documented.
