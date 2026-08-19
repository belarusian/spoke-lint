"""Tests for spoke_lint.diff: diff_invocation and diff_prompt (TICKET-018)."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

from spoke_lint.diff import diff_invocation, diff_prompt
from spoke_lint.models import ArgSpec, Finding, Invocation

FIXTURES = Path(__file__).parent / "fixtures"


class TestFindingModel:
    def test_is_frozen(self):
        f = Finding("unknown_flag", "x", "msg")
        with pytest.raises(dataclasses.FrozenInstanceError):
            f.kind = "other"  # type: ignore[misc]

    def test_is_hashable_and_equal(self):
        a = Finding("unknown_flag", "x", "msg")
        b = Finding("unknown_flag", "x", "msg")
        assert isinstance(hash(a), int)
        assert hash(a) == hash(b)
        assert a == b

    def test_fields_present(self):
        f = Finding("missing_required", "topic", "Required flag --topic missing")
        assert f.kind == "missing_required"
        assert f.flag == "topic"
        assert f.message == "Required flag --topic missing"


class TestDiffInvocation:
    def test_fully_valid_yields_no_findings(self):
        inv = Invocation("x/spokes/required_flag.py", (("--topic", "hi"),))
        specs = [ArgSpec(name="topic", required=True)]
        assert diff_invocation(inv, specs) == []

    def test_unknown_flag_detected(self):
        inv = Invocation("x/spokes/required_flag.py", (("--topic", "hi"), ("--bogus", "z")))
        specs = [ArgSpec(name="topic", required=True)]
        findings = diff_invocation(inv, specs)
        assert len(findings) == 1
        assert findings[0].kind == "unknown_flag"
        assert findings[0].flag == "bogus"

    def test_missing_required_detected(self):
        inv = Invocation("x/spokes/required_flag.py", ())
        specs = [ArgSpec(name="topic", required=True)]
        findings = diff_invocation(inv, specs)
        assert len(findings) == 1
        assert findings[0].kind == "missing_required"
        assert findings[0].flag == "topic"

    def test_optional_arg_not_flagged_when_absent(self):
        inv = Invocation("x/spokes/multi_args.py", (("--alpha", "a"),))
        specs = [
            ArgSpec(name="alpha", required=True),
            ArgSpec(name="beta", required=False, default="42"),
            ArgSpec(name="gamma", required=False),
        ]
        findings = diff_invocation(inv, specs)
        assert findings == []

    def test_unknown_before_missing_in_order(self):
        # Unknown-flag findings come first (invocation order), then
        # missing-required findings (signature order).
        inv = Invocation("x/spokes/multi_args.py", (("--bogus", "z"),))
        specs = [
            ArgSpec(name="alpha", required=True),
            ArgSpec(name="beta", required=False, default="42"),
        ]
        findings = diff_invocation(inv, specs)
        assert [f.kind for f in findings] == ["unknown_flag", "missing_required"]
        assert [f.flag for f in findings] == ["bogus", "alpha"]

    def test_multiple_unknown_flags_in_invocation_order(self):
        inv = Invocation("x/spokes/no_args.py", (("--z", "1"), ("--a", "2")))
        specs: list[ArgSpec] = []
        findings = diff_invocation(inv, specs)
        assert [f.flag for f in findings] == ["z", "a"]
        assert all(f.kind == "unknown_flag" for f in findings)


class TestDiffPrompt:
    def test_fully_valid_prompt_yields_no_findings(self):
        text = "python3 /a/spokes/required_flag.py --topic hi"
        assert diff_prompt(text, FIXTURES) == []

    def test_unknown_flag_through_pipeline(self):
        text = "python3 /a/spokes/required_flag.py --topic hi --bogus z"
        findings = diff_prompt(text, FIXTURES)
        assert len(findings) == 1
        assert findings[0].kind == "unknown_flag"
        assert findings[0].flag == "bogus"

    def test_missing_required_through_pipeline(self):
        text = "python3 /a/spokes/required_flag.py"
        findings = diff_prompt(text, FIXTURES)
        assert len(findings) == 1
        assert findings[0].kind == "missing_required"
        assert findings[0].flag == "topic"

    def test_multiple_invocations_aggregate_in_document_order(self):
        text = (
            "python3 /a/spokes/required_flag.py --bogus z\n"
            "some prose in between\n"
            "python3 /a/spokes/multi_args.py\n"
        )
        findings = diff_prompt(text, FIXTURES)
        # First invocation: unknown_flag(bogus) then missing_required(topic).
        # Second invocation: missing_required(alpha).
        assert [(f.kind, f.flag) for f in findings] == [
            ("unknown_flag", "bogus"),
            ("missing_required", "topic"),
            ("missing_required", "alpha"),
        ]

    def test_missing_script_yields_finding_not_exception(self):
        text = "python3 /a/spokes/does-not-exist.py --topic hi"
        findings = diff_prompt(text, FIXTURES)
        assert len(findings) == 1
        assert findings[0].kind == "missing_script"
        assert findings[0].flag == "/a/spokes/does-not-exist.py"

    def test_missing_script_does_not_abort_later_invocations(self):
        text = (
            "python3 /a/spokes/does-not-exist.py --topic hi\n"
            "python3 /a/spokes/required_flag.py\n"
        )
        findings = diff_prompt(text, FIXTURES)
        assert [(f.kind, f.flag) for f in findings] == [
            ("missing_script", "/a/spokes/does-not-exist.py"),
            ("missing_required", "topic"),
        ]

    def test_empty_prompt_yields_no_findings(self):
        assert diff_prompt("", FIXTURES) == []
        assert diff_prompt("just some prose\nno invocations", FIXTURES) == []
