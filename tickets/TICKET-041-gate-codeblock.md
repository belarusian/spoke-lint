# TICKET-041 — gate.py: skip fenced code blocks in gate_commands

**Cycle:** 14
**Module:** spoke_lint/gate.py

## Capability
Make gate_commands markdown-aware: iterate lines via spoke_lint.markdown.iter_lines_outside_code_blocks so a gate tool line (e.g. pytest) INSIDE a fenced code block is NOT detected. Lines OUTSIDE fenced blocks are processed exactly as today (env prefixes, python-interpreter skip, command-like check). diff_gate_commands behavior is unchanged (it consumes gate_commands output). Pure and deterministic; no I/O.
