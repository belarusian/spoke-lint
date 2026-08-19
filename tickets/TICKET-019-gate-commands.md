# TICKET-019 — gate_commands: extract leading executable of shell gate lines

**Cycle:** 6 (Diffing phase, Build Order phase 5)
**Module:** `spoke_lint/gate.py` (new)

## Capability
`gate_commands(text: str) -> list[str]`: return the **leading executable** of each
shell "gate" command line in a runner prompt, in document order.

A gate line is a non-blank, non-comment line whose first *command* token is a bare
command name (optionally preceded by `VAR=value ...` env-var prefixes). It must NOT
start with a python interpreter (`python`/`python3`/absolute `/.../python`) — those
are spoke invocation lines, not gate commands.

## Rules
- Strip leading whitespace; skip blank lines and lines starting with `#`.
- Skip tokens matching `\w+=\S+` (env-var prefixes) before the command.
- If the first non-prefix token is a python interpreter (`python`, `python3`, or an
  absolute path ending in `/python`/`/python3`) → NOT a gate line; skip.
- Otherwise the first remaining token is the executable name; strip any trailing
  punctuation that is not part of a bare command (keep it simple: take the raw token).
- Return names in document order (duplicates preserved, no dedup).

## Acceptance
- `pytest tests/ -x -q` → `["pytest"]`
- `FOO=bar ruff check spoke_lint/` → `["ruff"]`
- `python ~/spokes/x.py --goal hi` → `[]` (skipped)
- `# comment line` / blank → skipped
