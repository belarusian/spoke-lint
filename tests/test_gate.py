"""Tests for spoke_lint.gate: gate_commands and diff_gate_commands (TICKET-019/020/021/022).

All PATH-dependent tests are hermetic: they build a temp directory containing a
fake executable and point ``PATH`` at it via ``monkeypatch.setenv`` so the
results never depend on the host's real ``PATH``.
"""

from __future__ import annotations

import stat
from pathlib import Path

from spoke_lint.diff import diff_prompt
from spoke_lint.gate import diff_gate_commands, gate_commands
from spoke_lint.models import Finding

FIXTURES = Path(__file__).parent / "fixtures"


def _make_executable(path: Path) -> None:
    """Create an executable file at ``path`` (empty body, +x bit set)."""
    path.write_text("#!/bin/sh\nexit 0\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


class TestGateCommands:
    def test_single_tool_extracted(self):
        assert gate_commands("pytest") == ["pytest"]

    def test_multiple_tools_in_document_order(self):
        text = "pytest\nruff check spoke_lint/\nmypy spoke_lint/"
        assert gate_commands(text) == ["pytest", "ruff", "mypy"]

    def test_duplicates_preserved_no_dedup(self):
        assert gate_commands("pytest\npytest") == ["pytest", "pytest"]

    def test_env_var_prefixes_skipped(self):
        assert gate_commands("FOO=bar ruff check spoke_lint/") == ["ruff"]

    def test_multiple_env_var_prefixes_skipped(self):
        assert gate_commands("A=1 B=2 mypy spoke_lint/") == ["mypy"]

    def test_python_invocation_not_a_gate_command(self):
        assert gate_commands("python ~/spokes/x.py --goal hi") == []

    def test_python3_invocation_not_a_gate_command(self):
        assert gate_commands("python3 /a/spokes/x.py --goal hi") == []

    def test_absolute_python_path_not_a_gate_command(self):
        assert gate_commands("/usr/bin/python3 /a/spokes/x.py --goal hi") == []

    def test_comment_lines_skipped(self):
        assert gate_commands("# run the gates\npytest") == ["pytest"]

    def test_blank_lines_skipped(self):
        assert gate_commands("\n\npytest\n\n") == ["pytest"]

    def test_prose_lines_ignored(self):
        # Free-form prose is not a command line.
        assert gate_commands("just some prose\nno invocations") == []

    def test_mixed_prompt(self):
        text = (
            "# gate first\n"
            "pytest\n"
            "FOO=bar ruff check spoke_lint/\n"
            "python3 /a/spokes/required_flag.py --topic hi\n"
            "mypy spoke_lint/\n"
        )
        assert gate_commands(text) == ["pytest", "ruff", "mypy"]


class TestDiffGateCommands:
    def test_tool_present_yields_no_finding(self, tmp_path, monkeypatch):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _make_executable(bin_dir / "pytest")
        monkeypatch.setenv("PATH", str(bin_dir))
        assert diff_gate_commands("pytest") == []

    def test_tool_absent_yields_missing_tool(self, tmp_path, monkeypatch):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()  # empty: nothing resolvable
        monkeypatch.setenv("PATH", str(bin_dir))
        findings = diff_gate_commands("pytest")
        expected = Finding(
            kind="missing_tool",
            flag="pytest",
            message="Gate tool not found on PATH: pytest",
        )
        assert findings == [expected]

    def test_explicit_path_list_used(self, tmp_path):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _make_executable(bin_dir / "ruff")
        # Present tool -> no finding; absent tool -> finding.
        assert diff_gate_commands("ruff", path=[str(bin_dir)]) == []
        findings = diff_gate_commands("mypy", path=[str(bin_dir)])
        assert [f.kind for f in findings] == ["missing_tool"]
        assert [f.flag for f in findings] == ["mypy"]

    def test_document_order_preserved(self, tmp_path, monkeypatch):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        monkeypatch.setenv("PATH", str(bin_dir))
        findings = diff_gate_commands("pytest\nruff\nmypy")
        assert [f.flag for f in findings] == ["pytest", "ruff", "mypy"]
        assert all(f.kind == "missing_tool" for f in findings)

    def test_no_side_effects_on_env(self, tmp_path, monkeypatch):
        # Passing an explicit path must not read or mutate the environment.
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        monkeypatch.setenv("PATH", "/definitely/not/here")
        _make_executable(bin_dir / "pytest")
        assert diff_gate_commands("pytest", path=[str(bin_dir)]) == []


class TestDiffPromptGateIntegration:
    def test_gate_findings_appended_after_invocation_findings(self, tmp_path, monkeypatch):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()  # empty PATH: gate tool absent
        monkeypatch.setenv("PATH", str(bin_dir))
        text = (
            "python3 /a/spokes/required_flag.py --bogus z\n"
            "pytest\n"
        )
        findings = diff_prompt(text, FIXTURES)
        # Invocation findings first (unknown_flag bogus, missing_required topic),
        # then the gate-command finding (missing_tool pytest).
        assert [(f.kind, f.flag) for f in findings] == [
            ("unknown_flag", "bogus"),
            ("missing_required", "topic"),
            ("missing_tool", "pytest"),
        ]

    def test_fully_valid_prompt_on_matching_path_yields_no_findings(self, tmp_path, monkeypatch):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _make_executable(bin_dir / "pytest")
        monkeypatch.setenv("PATH", str(bin_dir))
        text = (
            "python3 /a/spokes/required_flag.py --topic hi\n"
            "pytest\n"
        )
        assert diff_prompt(text, FIXTURES) == []

    def test_two_arg_call_still_works(self, tmp_path, monkeypatch):
        # The original two-arg signature must keep working; path defaults to
        # the environment PATH.
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _make_executable(bin_dir / "pytest")
        monkeypatch.setenv("PATH", str(bin_dir))
        text = "python3 /a/spokes/required_flag.py --topic hi\npytest"
        assert diff_prompt(text, FIXTURES) == []

    def test_two_arg_call_flags_absent_gate_tool(self, tmp_path, monkeypatch):
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()  # empty: pytest absent
        monkeypatch.setenv("PATH", str(bin_dir))
        text = "python3 /a/spokes/required_flag.py --topic hi\npytest"
        findings = diff_prompt(text, FIXTURES)
        assert [(f.kind, f.flag) for f in findings] == [("missing_tool", "pytest")]
