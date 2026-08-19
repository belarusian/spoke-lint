# TICKET-021 — extend diff_prompt with optional path (gate findings)

**Cycle:** 6 (Diffing phase, Build Order phase 5)
**Module:** `spoke_lint/diff.py`

## Capability
Extend `diff_prompt(text: str, spokes_dir: Path, path: list[str] | None = None) -> list[Finding]`
to ALSO append `diff_gate_commands(text, path)` findings **after** the invocation
findings. Deterministic order: invocation findings first, then gate-command findings.

## Rules
- Keep the existing two-arg call working (`path` defaults to the environment PATH).
- Do not change any existing invocation-finding behavior (non-regressing).
- Import `diff_gate_commands` from `spoke_lint.gate`.

## Acceptance
- A prompt with a valid invocation + an absent gate tool → [invocation findings..., missing_tool].
- A fully-valid prompt on a PATH containing the tools → [].
