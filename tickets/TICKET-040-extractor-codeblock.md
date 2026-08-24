# TICKET-040 — extractor.py: skip fenced code blocks in extract_invocations

**Cycle:** 14
**Module:** spoke_lint/extractor.py

## Capability
Make extract_invocations markdown-aware: iterate lines via spoke_lint.markdown.iter_lines_outside_code_blocks so a spoke invocation line INSIDE a fenced code block is NOT extracted. Lines OUTSIDE fenced blocks are processed exactly as today (python interpreter + a /spokes/ path -> Invocation). Pure and deterministic; no I/O. Do not change how a real (non-code-block) invocation is parsed.
