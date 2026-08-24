"""End-to-end markdown-awareness tests (TICKET-043).

These tests drive the full pipeline (extraction -> parsing -> diffing -> gate
checking) against prompts that contain fenced markdown code blocks, proving that
illustrative tool calls shown inside a fenced block produce NO findings, while
the same lines outside a code block produce the expected findings.
"""

from __future__ import annotations

from pathlib import Path

from spoke_lint.diff import diff_prompt_full
from spoke_lint.models import Finding

FIXTURES = Path(__file__).parent / "fixtures"

# A fenced block containing a fake spoke invocation and a fake gate line.
FENCED_PROMPT = (
    "```\n"
    "python3 /a/spokes/ghost.py --x y\n"
    "pytest\n"
    "```\n"
)

# The same lines, but OUTSIDE any code block.
BARE_PROMPT = (
    "python3 /a/spokes/ghost.py --x y\n"
    "pytest\n"
)


class TestFencedCodeBlockEndToEnd:
    def test_fenced_block_yields_no_findings_on_empty_path(
        self, tmp_path, monkeypatch
    ):
        # A fenced code block containing a fake spoke invocation and a fake
        # gate line yields NO findings (the block is ignored), even on an empty
        # PATH.
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()  # empty: nothing resolvable
        monkeypatch.setenv("PATH", str(bin_dir))
        findings = diff_prompt_full(FENCED_PROMPT, FIXTURES)
        assert findings == []

    def test_bare_lines_outside_block_yield_expected_findings(
        self, tmp_path, monkeypatch
    ):
        # The same lines OUTSIDE a code block yield the expected findings
        # (regression guard): a missing_script for the unresolvable ghost.py
        # and a missing_tool for pytest on an empty PATH.
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()  # empty: nothing resolvable
        monkeypatch.setenv("PATH", str(bin_dir))
        findings = diff_prompt_full(BARE_PROMPT, FIXTURES)
        expected = [
            Finding(
                kind="missing_script",
                flag="/a/spokes/ghost.py",
                message="Referenced script not found: /a/spokes/ghost.py",
            ),
            Finding(
                kind="missing_tool",
                flag="pytest",
                message="Gate tool not found on PATH: pytest",
            ),
        ]
        assert findings == expected

    def test_fenced_and_bare_differ(self, tmp_path, monkeypatch):
        # The fenced prompt is clean while the bare prompt has findings, so the
        # markdown-awareness is what suppresses the findings.
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        monkeypatch.setenv("PATH", str(bin_dir))
        fenced = diff_prompt_full(FENCED_PROMPT, FIXTURES)
        bare = diff_prompt_full(BARE_PROMPT, FIXTURES)
        assert fenced == []
        assert len(bare) == 2
