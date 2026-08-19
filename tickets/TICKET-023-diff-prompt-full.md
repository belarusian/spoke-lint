# TICKET-023 — diff_prompt_full: explicit full-pipeline entry point

**Cycle:** 7 (Diffing phase completion, Build Order phase 5)
**Module:** `spoke_lint/diff.py`

## Capability
`diff_prompt_full(text: str, spokes_dir: Path, path: list[str] | None = None) -> list[Finding]`:
a named convenience that runs the full pipeline — invocation findings **plus**
gate-command findings — in one deterministic pass.

It delegates to `diff_prompt` (which already appends gate-command findings after
invocation findings). Document that delegation explicitly so the entry point is a
stable, self-documenting name for callers/CLI rather than an implementation detail.

## Rules
- Signature mirrors `diff_prompt` exactly (`text`, `spokes_dir`, `path=None`).
- Body: `return diff_prompt(text, spokes_dir, path)`.
- Do NOT change any existing behavior; this is a pure alias with documentation.
- Deterministic ordering inherited from `diff_prompt`: invocation findings first
  (document order), then gate-command findings (document order).

## Acceptance
- For identical inputs, `diff_prompt_full(t, d, p) == diff_prompt(t, d, p)` for all
  finding kinds (missing_script / unknown_flag / missing_required / missing_tool).
- Two-arg call works: `diff_prompt_full(t, d)` uses the environment PATH.
