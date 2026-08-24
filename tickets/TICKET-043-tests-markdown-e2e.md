# TICKET-043 — tests/test_markdown.py: end-to-end fenced-code-block tests

**Cycle:** 14
**Module:** tests/test_markdown.py (new)

## Capability
End-to-end: a prompt with a fenced code block containing a fake spoke invocation (python3 /a/spokes/ghost.py --x y) and a fake gate line (pytest) yields NO findings (the block is ignored), even on an empty PATH. A prompt with the same lines OUTSIDE a code block yields the expected findings (regression guard). Hermetic (tmp_path, explicit --path / monkeypatch.setenv for the gate case).
