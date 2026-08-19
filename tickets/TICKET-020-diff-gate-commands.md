# TICKET-020 — diff_gate_commands: flag tools not on PATH

**Cycle:** 6 (Diffing phase, Build Order phase 5)
**Module:** `spoke_lint/gate.py` (new)

## Capability
`diff_gate_commands(text: str, path: list[str] | None = None) -> list[Finding]`:
for each executable from `gate_commands(text)`, resolve it against `path` (default
`os.environ["PATH"]`) using `shutil.which`. If not found, emit
`Finding("missing_tool", <name>, message)` in document order.

## Rules
- Reuse the existing frozen `Finding` dataclass (kind `"missing_tool"`); no new model.
- `path=None` → use `os.environ["PATH"]`.
- Pure/deterministic; no side effects; stable ordering matches `gate_commands`.
- Message should name the tool and note it was not found on PATH.

## Acceptance
- Tool present on a hermetic temp-dir PATH → no finding.
- Tool absent from PATH → one `missing_tool` finding with `flag == <name>`.
