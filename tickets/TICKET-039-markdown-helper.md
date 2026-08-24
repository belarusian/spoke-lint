# TICKET-039 — markdown.py: shared fenced-code-block helper

**Cycle:** 14
**Module:** spoke_lint/markdown.py (new, stdlib-only)

## Capability
Provide iter_lines_outside_code_blocks(text) -> Iterator[tuple[int, str]] yielding only lines OUTSIDE fenced markdown code blocks as (original_0_based_index, line). A line whose stripped form starts with three backticks (optionally followed by a language tag) toggles in/out of a code block. While inside a fenced code block (including the fence delimiter lines themselves), the line is NOT yielded. An unclosed fence ignores everything after the opening fence. A language-tagged fence is handled the same as a bare fence. stdlib-only; pure and deterministic; no I/O.
