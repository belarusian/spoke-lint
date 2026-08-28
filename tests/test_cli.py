"""Tests for spoke_lint.cli: build_parser, run, and the exit-code contract (TICKET-031..033).

All tests are hermetic: they write prompt files under ``tmp_path`` and call
``run([...])`` in-process (no subprocesses), capturing stdout/stderr with
``capsys``. The CLI is a **subcommand** interface, so every invocation argv is
prefixed with the ``check`` subcommand. The gate-tool case uses a temp-dir fake
executable plus an explicit ``--path`` so it never depends on the host's real PATH.
"""

from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest

from spoke_lint.cli import build_parser, run
from spoke_lint.models import Finding
from spoke_lint.report import render_report

FIXTURES = Path(__file__).parent / "fixtures"


def _write_prompt(tmp_path: Path, text: str) -> Path:
    prompt = tmp_path / "prompt.txt"
    prompt.write_text(text, encoding="utf-8")
    return prompt


def _make_executable(path: Path) -> None:
    path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


class TestBuildParser:
    def test_returns_argparse_parser(self):
        import argparse

        assert isinstance(build_parser(), argparse.ArgumentParser)

    def test_defaults(self):
        ns = build_parser().parse_args(["check", "prompt.txt"])
        assert ns.command == "check"
        assert ns.prompt_file == "prompt.txt"
        assert ns.spokes_dir == "./spokes"
        assert ns.path is None

    def test_explicit_options(self):
        ns = build_parser().parse_args(
            ["check", "p.txt", "--spokes-dir", "D", "--path", "a,b"]
        )
        assert ns.command == "check"
        assert ns.prompt_file == "p.txt"
        assert ns.spokes_dir == "D"
        assert ns.path == "a,b"

    def test_subcommand_is_required(self):
        # A call with no subcommand is a usage error: argparse exits non-zero.
        with pytest.raises(SystemExit) as exc:
            build_parser().parse_args([])
        assert exc.value.code != 0


class TestRunClean:
    def test_valid_prompt_exit_0_stdout_ok(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, "python3 /a/spokes/no_args.py\n")
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        assert code == 0
        out = capsys.readouterr().out
        assert out.strip() == "OK"


class TestRunFindings:
    def test_unknown_flag_exit_1_report(self, tmp_path, capsys):
        cmd = "python3 /a/spokes/required_flag.py --topic hi --bogus z\n"
        prompt = _write_prompt(tmp_path, cmd)
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        assert code == 1
        out = capsys.readouterr().out
        expected = render_report(
            [
                Finding(
                    "unknown_flag",
                    "bogus",
                    "Unknown flag --bogus passed to /a/spokes/required_flag.py",
                )
            ]
        )
        assert out.strip() == expected

    def test_missing_required_exit_1_report(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, "python3 /a/spokes/required_flag.py\n")
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        assert code == 1
        out = capsys.readouterr().out
        assert "missing_required" in out
        assert "topic" in out

    def test_missing_script_exit_1(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, "python3 /a/spokes/does-not-exist.py --topic hi\n")
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        assert code == 1
        out = capsys.readouterr().out
        assert "missing_script" in out
        assert "/a/spokes/does-not-exist.py" in out


class TestRunGateTool:
    def test_missing_tool_exit_1_via_path(self, tmp_path, capsys):
        # A gate line referencing a tool; point --path at an empty temp dir so it
        # is not resolvable. Hermetic: no host-PATH dependence.
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        prompt = _write_prompt(tmp_path, "pytest tests/ -x -q\n")
        code = run(
            ["check", str(prompt), "--spokes-dir", str(FIXTURES), "--path", str(empty_dir)]
        )
        assert code == 1
        out = capsys.readouterr().out
        assert "missing_tool" in out
        assert "pytest" in out

    def test_present_tool_no_finding_via_path(self, tmp_path, capsys):
        # A fake executable on the explicit --path resolves cleanly -> no findings.
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        _make_executable(bin_dir / "pytest")
        prompt = _write_prompt(tmp_path, "pytest tests/ -x -q\n")
        code = run(
            ["check", str(prompt), "--spokes-dir", str(FIXTURES), "--path", str(bin_dir)]
        )
        assert code == 0
        out = capsys.readouterr().out
        assert out.strip() == "OK"


class TestRunIOError:
    def test_missing_prompt_file_exit_2_stderr(self, tmp_path, capsys):
        missing = tmp_path / "nope.txt"
        code = run(["check", str(missing), "--spokes-dir", str(FIXTURES)])
        assert code == 2
        err = capsys.readouterr().err
        assert "cannot read prompt file" in err
        # No exception escaped; stdout is empty.
        assert capsys.readouterr().out == ""


class TestRunPathSplitting:
    def test_path_comma_split_and_whitespace(self, tmp_path, capsys):
        # Two comma-separated dirs with surrounding whitespace; the tool lives in
        # the second dir so it resolves -> clean.
        bin_dir = tmp_path / "bin2"
        bin_dir.mkdir()
        _make_executable(bin_dir / "ruff")
        other = tmp_path / "other"
        other.mkdir()
        prompt = _write_prompt(tmp_path, "ruff check spoke_lint/\n")
        code = run(
            [
                "check",
                str(prompt),
                "--spokes-dir",
                str(FIXTURES),
                "--path",
                f"{other}, {bin_dir}",
            ]
        )
        assert code == 0
        assert capsys.readouterr().out.strip() == "OK"


class TestRunSubcommandErrors:
    def test_no_subcommand_nonzero_no_traceback(self, capsys):
        # A call with no subcommand is a usage error -> non-zero (typically 2),
        # and run must not raise.
        code = run([])
        assert code != 0
        assert code == 2
        # argparse printed its usage/error to stderr; nothing on stdout.
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "check" in captured.err or "usage" in captured.err.lower()

    def test_unknown_subcommand_nonzero_no_traceback(self, tmp_path, capsys):
        # An unrecognized subcommand is a usage error -> non-zero (typically 2),
        # and run must not raise.
        prompt = _write_prompt(tmp_path, "python3 /a/spokes/no_args.py\n")
        code = run(["bogus", str(prompt)])
        assert code != 0
        assert code == 2
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "bogus" in captured.err or "usage" in captured.err.lower()


class TestMainGuard:
    def test_main_exits_with_run_code(self, tmp_path, monkeypatch):
        # main() calls sys.exit(run()); verify it propagates the exit code.
        prompt = _write_prompt(tmp_path, "python3 /a/spokes/no_args.py\n")
        with pytest.raises(SystemExit) as exc:
            from spoke_lint.cli import main

            monkeypatch.setattr(
                "sys.argv", ["spoke-lint", "check", str(prompt), "--spokes-dir", str(FIXTURES)]
            )
            main()
        assert exc.value.code == 0


class TestRunJson:
    def test_json_flag_default_false(self):
        ns = build_parser().parse_args(["check", "p.txt"])
        assert ns.json is False

    def test_json_flag_true_when_given(self):
        ns = build_parser().parse_args(["check", "p.txt", "--json"])
        assert ns.json is True

    def test_clean_prompt_json_exit_0_empty_array(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, "python3 /a/spokes/no_args.py\n")
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES), "--json"])
        assert code == 0
        out = capsys.readouterr().out
        assert out.strip() == "[]"
        assert json.loads(out) == []

    def test_unknown_flag_json_exit_1_valid_json(self, tmp_path, capsys):
        cmd = "python3 /a/spokes/required_flag.py --topic hi --bogus z\n"
        prompt = _write_prompt(tmp_path, cmd)
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES), "--json"])
        assert code == 1
        out = capsys.readouterr().out
        parsed = json.loads(out)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        first = parsed[0]
        assert set(first.keys()) == {"kind", "flag", "message"}
        assert first["kind"] == "unknown_flag"
        assert first["flag"] == "bogus"
        assert "--bogus" in first["message"]

    def test_missing_prompt_file_json_exit_2_stderr(self, tmp_path, capsys):
        missing = tmp_path / "nope.txt"
        code = run(["check", str(missing), "--spokes-dir", str(FIXTURES), "--json"])
        assert code == 2
        captured = capsys.readouterr()
        assert "cannot read prompt file" in captured.err
        # No exception escaped; stdout is empty.
        assert captured.out == ""

    def test_json_output_matches_findings_to_json(self, tmp_path, capsys):
        # The --json payload must be byte-identical to findings_to_json of the
        # same findings (the CLI stays a thin orchestration layer).
        from spoke_lint.report import findings_to_json

        cmd = "python3 /a/spokes/required_flag.py --topic hi --bogus z\n"
        prompt = _write_prompt(tmp_path, cmd)
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES), "--json"])
        assert code == 1
        out = capsys.readouterr().out
        expected = findings_to_json(
            [
                Finding(
                    "unknown_flag",
                    "bogus",
                    "Unknown flag --bogus passed to /a/spokes/required_flag.py",
                )
            ]
        )
        assert out.strip() == expected


class TestRunNotRunnerPrompt:
    """Issue #60: a pure shell / non-runner-prompt input is rejected with exit 2
    and a single diagnostic line, not a ``missing_tool`` flood."""

    def test_shell_script_exit_2_single_diagnostic(self, tmp_path, capsys):
        prompt = _write_prompt(
            tmp_path,
            "#!/bin/bash\nset -uo pipefail\nexport FIVE_MODEL=x\n"
            "INNER=$(cat <<'EOF'\nhello\nEOF\n)\n",
        )
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        assert code == 2
        err = capsys.readouterr().err
        assert "not a runner prompt" in err
        # Exactly one diagnostic line on stderr (no missing_tool flood).
        assert err.strip().count("\n") == 0
        # Nothing on stdout.
        assert capsys.readouterr().out == ""

    def test_launch_setup_fixture_exit_2(self, tmp_path, capsys):
        fixture = FIXTURES / "launch_setup.sh"
        code = run(["check", str(fixture), "--spokes-dir", str(FIXTURES)])
        assert code == 2
        err = capsys.readouterr().err
        assert "not a runner prompt" in err
        assert "missing_tool" not in err

    def test_runner_prompt_with_fenced_shell_still_lints(self, tmp_path, capsys):
        # A runner prompt that embeds shell in a fenced block is still linted
        # (not rejected); here it is clean -> exit 0.
        fence = chr(96) * 3
        prompt = _write_prompt(
            tmp_path,
            "Run the gate:\n" + fence + "\n"
            + "set -uo pipefail\nexport FIVE_MODEL=x\n"
            + fence + "\n"
            + "Then run the spoke\n"
            + "python3 /a/spokes/no_args.py\n",
        )
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        assert code == 0
        assert capsys.readouterr().out.strip() == "OK"
