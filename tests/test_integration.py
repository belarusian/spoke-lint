"""End-to-end integration tests for spoke-lint (Cycle 11).

These drive the *whole* pipeline — extraction -> parsing -> diffing ->
reporting/JSON — through the CLI's ``run([...])`` in-process (no subprocesses),
capturing stdout/stderr with ``capsys``. Prompts are written under ``tmp_path``
and reference the existing spoke fixtures, so the tests are hermetic and never
depend on the host PATH (any gate-tool case uses an explicit ``--path``).

They guard that the layers compose correctly end-to-end: the exit-code contract
(0 = clean / 1 = findings / 2 = usage-IO error) and the deterministic report/JSON
output hold not just per-function but across the full CLI surface.
"""

from __future__ import annotations

import json
from pathlib import Path

from spoke_lint.cli import run
from spoke_lint.models import Finding
from spoke_lint.report import _KIND_ORDER, findings_to_json, render_report

FIXTURES = Path(__file__).parent / "fixtures"


def _write_prompt(tmp_path: Path, text: str) -> Path:
    prompt = tmp_path / "prompt.txt"
    prompt.write_text(text, encoding="utf-8")
    return prompt


# A realistic multi-line runner prompt mixing a clean invocation with one unknown
# flag and one missing required flag. The script paths carry the ``/spokes/``
# segment the extractor requires; basenames resolve against FIXTURES.
MIXED_PROMPT = (
    "Now run the full pipeline\n"
    "python3 /a/spokes/no_args.py --topic hi\n"
    "python3 /a/spokes/required_flag.py\n"
)

# A fully-clean multi-invocation prompt: every invocation is valid and there are
# no gate-command lines, so the report must be "OK".
CLEAN_PROMPT = (
    "Now run the full pipeline\n"
    "python3 /a/spokes/no_args.py\n"
    "python3 /a/spokes/required_flag.py --topic hello\n"
    "python3 /a/spokes/multi_args.py --alpha x --beta 7\n"
)


def _expected_mixed_findings() -> list[Finding]:
    """The exact findings the mixed prompt produces, in document order."""
    return [
        Finding(
            kind="unknown_flag",
            flag="topic",
            message="Unknown flag --topic passed to /a/spokes/no_args.py",
        ),
        Finding(
            kind="missing_required",
            flag="topic",
            message="Required flag --topic missing from /a/spokes/required_flag.py",
        ),
    ]


class TestEndToEndHumanReport:
    def test_mixed_prompt_exit_1_report_lines_in_kind_order(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, MIXED_PROMPT)
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        assert code == 1
        out = capsys.readouterr().out

        expected = render_report(_expected_mixed_findings())
        # The CLI prints the report verbatim (plus a trailing newline from print).
        assert out.rstrip("\n") == expected

        lines = out.splitlines()
        # Each line is "<kind>: <flag> — <message>"; verify the kinds appear in
        # the documented _KIND_ORDER grouping order.
        kinds_in_output = [line.split(":", 1)[0] for line in lines]
        assert kinds_in_output == ["unknown_flag", "missing_required"]
        # And that ordering is a subsequence of _KIND_ORDER (stable grouping).
        positions = [_KIND_ORDER.index(k) for k in kinds_in_output if k in _KIND_ORDER]
        assert positions == sorted(positions)

    def test_clean_multi_invocation_prompt_exit_0_ok(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, CLEAN_PROMPT)
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        assert code == 0
        out = capsys.readouterr().out
        assert out.strip() == "OK"


class TestEndToEndJson:
    def test_mixed_prompt_json_exit_1_matches_findings(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, MIXED_PROMPT)
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES), "--json"])
        assert code == 1
        out = capsys.readouterr().out

        parsed = json.loads(out)
        assert isinstance(parsed, list)
        expected = _expected_mixed_findings()
        assert len(parsed) == len(expected)
        for obj, finding in zip(parsed, expected, strict=True):
            assert set(obj.keys()) == {"kind", "flag", "message"}
            assert obj["kind"] == finding.kind
            assert obj["flag"] == finding.flag
            assert obj["message"] == finding.message

    def test_mixed_prompt_json_byte_identical_to_findings_to_json(self, tmp_path, capsys):
        # The CLI's JSON payload must be exactly findings_to_json of the same
        # findings — proving the CLI stays a thin orchestration layer.
        prompt = _write_prompt(tmp_path, MIXED_PROMPT)
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES), "--json"])
        assert code == 1
        out = capsys.readouterr().out
        expected = findings_to_json(_expected_mixed_findings())
        assert out.rstrip("\n") == expected

    def test_clean_multi_invocation_prompt_json_exit_0_empty_array(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, CLEAN_PROMPT)
        code = run(["check", str(prompt), "--spokes-dir", str(FIXTURES), "--json"])
        assert code == 0
        out = capsys.readouterr().out
        assert out.strip() == "[]"
        assert json.loads(out) == []


class TestEndToEndDeterminism:
    def test_human_report_byte_identical_across_runs(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, MIXED_PROMPT)
        first = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        out1 = capsys.readouterr().out
        second = run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        out2 = capsys.readouterr().out
        assert first == second == 1
        assert out1 == out2

    def test_json_output_byte_identical_across_runs(self, tmp_path, capsys):
        prompt = _write_prompt(tmp_path, MIXED_PROMPT)
        first = run(["check", str(prompt), "--spokes-dir", str(FIXTURES), "--json"])
        out1 = capsys.readouterr().out
        second = run(["check", str(prompt), "--spokes-dir", str(FIXTURES), "--json"])
        out2 = capsys.readouterr().out
        assert first == second == 1
        assert out1 == out2

    def test_human_and_json_consistent_for_same_prompt(self, tmp_path, capsys):
        # The human report and JSON payload must describe the *same* findings:
        # parsing the JSON and rendering it must reproduce the human report.
        prompt = _write_prompt(tmp_path, MIXED_PROMPT)
        run(["check", str(prompt), "--spokes-dir", str(FIXTURES)])
        human = capsys.readouterr().out
        run(["check", str(prompt), "--spokes-dir", str(FIXTURES), "--json"])
        js = capsys.readouterr().out

        parsed = json.loads(js)
        findings = [
            Finding(kind=o["kind"], flag=o["flag"], message=o["message"]) for o in parsed
        ]
        assert render_report(findings) == human.rstrip("\n")
