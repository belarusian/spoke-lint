"""Tests for spoke_lint.report: format_finding and render_report (TICKET-024/025).

Deterministic, pure-string tests. No I/O, no PATH dependence — findings are
constructed directly so the assertions are byte-stable.
"""

from __future__ import annotations

import json

import pytest

from spoke_lint.models import Finding
from spoke_lint.report import (
    _KIND_ORDER,
    findings_to_json,
    format_finding,
    render_report,
)


def _finding(kind: str, flag: str, message: str) -> Finding:
    return Finding(kind=kind, flag=flag, message=message)


class TestFormatFinding:
    def test_exact_line_format(self):
        f = _finding("unknown_flag", "bogus", "Unknown flag --bogus passed to x.py")
        assert format_finding(f) == (
            "unknown_flag: bogus — Unknown flag --bogus passed to x.py"
        )

    def test_stable_across_calls(self):
        f = _finding("missing_required", "topic", "Required flag --topic missing")
        assert format_finding(f) == format_finding(f)

    def test_no_trailing_newline(self):
        f = _finding("missing_tool", "ruff", "Tool ruff not on PATH")
        assert not format_finding(f).endswith("\n")


class TestRenderReportEmpty:
    def test_empty_returns_ok(self):
        assert render_report([]) == "OK"

    def test_ok_has_no_trailing_newline(self):
        assert render_report([]) == "OK"
        assert not render_report([]).endswith("\n")


class TestRenderReportSingle:
    def test_single_finding_one_line(self):
        f = _finding("missing_script", "x/spokes/nope.py", "Referenced script not found")
        report = render_report([f])
        assert report == format_finding(f)
        assert "\n" not in report

    def test_single_matches_format_finding(self):
        f = _finding("unknown_flag", "z", "msg")
        assert render_report([f]) == format_finding(f)


class TestRenderReportGrouping:
    def test_same_kind_preserves_input_order(self):
        a = _finding("unknown_flag", "a", "first")
        b = _finding("unknown_flag", "b", "second")
        c = _finding("unknown_flag", "c", "third")
        report = render_report([a, b, c])
        lines = report.split("\n")
        assert lines == [format_finding(a), format_finding(b), format_finding(c)]

    def test_mixed_kinds_group_in_stable_order(self):
        # Deliberately shuffled input: tool, required, script, flag.
        tool = _finding("missing_tool", "ruff", "Tool ruff not on PATH")
        req = _finding("missing_required", "topic", "Required flag --topic missing")
        script = _finding("missing_script", "x.py", "Referenced script not found")
        flag = _finding("unknown_flag", "bogus", "Unknown flag --bogus passed")

        report = render_report([tool, req, script, flag])
        lines = report.split("\n")
        # Expected order: missing_script, unknown_flag, missing_required, missing_tool.
        assert lines == [
            format_finding(script),
            format_finding(flag),
            format_finding(req),
            format_finding(tool),
        ]

    def test_kind_order_constant_matches_documentation(self):
        assert _KIND_ORDER == (
            "missing_script",
            "unknown_flag",
            "missing_required",
            "missing_tool",
        )


class TestRenderReportUnknownKind:
    def test_unknown_kind_appended_after_known_sorted(self):
        known = _finding("missing_tool", "ruff", "Tool ruff not on PATH")
        zeta = _finding("zeta_kind", "z", "a zeta finding")
        alpha = _finding("alpha_kind", "a", "an alpha finding")

        report = render_report([known, zeta, alpha])
        lines = report.split("\n")
        # Known group first (missing_tool), then unknown kinds sorted: alpha, zeta.
        assert lines == [
            format_finding(known),
            format_finding(alpha),
            format_finding(zeta),
        ]

    def test_only_unknown_kinds_sorted(self):
        b = _finding("beta_kind", "b", "beta")
        a = _finding("alpha_kind", "a", "alpha")
        report = render_report([b, a])
        assert report.split("\n") == [format_finding(a), format_finding(b)]


class TestRenderReportDeterminism:
    def test_byte_identical_across_calls(self):
        findings = [
            _finding("missing_tool", "ruff", "Tool ruff not on PATH"),
            _finding("unknown_flag", "bogus", "Unknown flag --bogus passed"),
            _finding("missing_required", "topic", "Required flag --topic missing"),
            _finding("missing_script", "x.py", "Referenced script not found"),
        ]
        assert render_report(findings) == render_report(list(findings))

    def test_every_line_is_a_formatted_finding(self):
        findings = [
            _finding("unknown_flag", "a", "m1"),
            _finding("missing_required", "b", "m2"),
            _finding("unknown_flag", "c", "m3"),
        ]
        report = render_report(findings)
        expected_lines = {format_finding(f) for f in findings}
        lines = report.split("\n")
        assert set(lines) == expected_lines
        # Each line corresponds to exactly one finding (no duplicates lost).
        assert len(lines) == len(findings)

    def test_grouping_is_stable_not_input_order(self):
        # Input order is tool, flag; output must be flag (unknown_flag) before tool.
        tool = _finding("missing_tool", "ruff", "Tool ruff not on PATH")
        flag = _finding("unknown_flag", "bogus", "Unknown flag --bogus passed")
        lines = render_report([tool, flag]).split("\n")
        assert lines[0] == format_finding(flag)
        assert lines[1] == format_finding(tool)


@pytest.mark.parametrize(
    "kind",
    ["missing_script", "unknown_flag", "missing_required", "missing_tool"],
)
def test_each_known_kind_renders(kind: str):
    f = _finding(kind, "flag", "message")
    assert render_report([f]) == format_finding(f)


class TestFindingsToJson:
    def test_empty_returns_empty_array(self):
        assert findings_to_json([]) == "[]"

    def test_single_finding_exact_keys_and_values(self):
        f = _finding("unknown_flag", "bogus", "Unknown flag --bogus passed to x.py")
        out = findings_to_json([f])
        parsed = json.loads(out)
        assert isinstance(parsed, list)
        assert len(parsed) == 1
        obj = parsed[0]
        assert set(obj.keys()) == {"kind", "flag", "message"}
        assert obj["kind"] == "unknown_flag"
        assert obj["flag"] == "bogus"
        assert obj["message"] == "Unknown flag --bogus passed to x.py"

    def test_multiple_preserves_input_order(self):
        a = _finding("missing_tool", "ruff", "Tool ruff not on PATH")
        b = _finding("unknown_flag", "z", "a flag finding")
        c = _finding("missing_required", "topic", "Required flag --topic missing")
        parsed = json.loads(findings_to_json([a, b, c]))
        assert [o["flag"] for o in parsed] == ["ruff", "z", "topic"]
        assert [o["kind"] for o in parsed] == [
            "missing_tool",
            "unknown_flag",
            "missing_required",
        ]

    def test_round_trips_to_same_field_values(self):
        findings = [
            _finding("missing_script", "x.py", "Referenced script not found"),
            _finding("unknown_flag", "a", "m1"),
        ]
        parsed = json.loads(findings_to_json(findings))
        for original, obj in zip(findings, parsed, strict=True):
            assert obj == {
                "kind": original.kind,
                "flag": original.flag,
                "message": original.message,
            }

    def test_byte_deterministic_across_calls(self):
        findings = [
            _finding("missing_tool", "ruff", "Tool ruff not on PATH"),
            _finding("unknown_flag", "bogus", "Unknown flag --bogus passed"),
        ]
        assert findings_to_json(findings) == findings_to_json(list(findings))

    def test_no_trailing_newline(self):
        f = _finding("missing_required", "topic", "Required flag --topic missing")
        assert not findings_to_json([f]).endswith("\n")

    def test_non_ascii_message_preserved(self):
        # ensure_ascii=False keeps non-ASCII characters as-is in the output.
        f = _finding("unknown_flag", "z", "caf\u00e9 message")
        out = findings_to_json([f])
        assert "caf\u00e9" in out
        assert json.loads(out)[0]["message"] == "caf\u00e9 message"
