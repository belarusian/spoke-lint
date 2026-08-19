# TICKET-017 — diff_prompt: top-level entry point

**Phase:** Diffing (Cycle 5)
**Module:** `spoke_lint/diff.py`
**Status:** open

## What
Add `diff_prompt(text: str, spokes_dir: Path) -> list[Finding]` to `spoke_lint/diff.py`.

This is the top-level entry point:
1. Extract invocations via `extract_invocations(text)` (document order).
2. For each invocation, resolve its script path against `spokes_dir`: take the basename
   of `invocation.script_path` and look for it under `spokes_dir`.
3. If the resolved script does not exist -> emit a single
   `Finding("missing_script", <script_path>, ...)` and continue (do NOT raise).
4. Otherwise parse its signature via `parse_spoke_args(resolved)` and append
   `diff_invocation(invocation, specs)`.

Aggregate findings across all invocations in deterministic order (invocation document
order; within an invocation, the ordering from TICKET-016).

## Why
This is what a user/CLI calls: give it a prompt string and a directory of spokes, get
back every problem. Graceful handling of missing scripts keeps one bad reference from
aborting the whole lint.

## Acceptance
- A valid invocation against an existing fixture yields `[]`.
- An unknown flag / missing required arg are surfaced through the full pipeline.
- Multiple invocations aggregate in document order.
- A referenced script that does not exist under `spokes_dir` yields a `missing_script`
  finding (not an exception).
