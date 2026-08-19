"""Tests for spoke_lint package-level public API (TICKET-004, 007, 010, 014, 018, 026, 030)."""

from __future__ import annotations


def test_public_api_importable():
    from spoke_lint import (
        ArgSpec,
        Finding,
        Invocation,
        build_parser,
        canonical_names,
        diff_gate_commands,
        diff_invocation,
        diff_prompt,
        diff_prompt_full,
        extract_invocations,
        findings_to_json,
        format_finding,
        gate_commands,
        parse_spoke,
        parse_spoke_args,
        render_report,
        run,
    )

    assert Invocation is not None
    assert ArgSpec is not None
    assert Finding is not None
    assert callable(extract_invocations)
    assert callable(parse_spoke_args)
    assert callable(parse_spoke)
    assert callable(canonical_names)
    assert callable(diff_invocation)
    assert callable(diff_prompt)
    assert callable(diff_prompt_full)
    assert callable(gate_commands)
    assert callable(diff_gate_commands)
    assert callable(findings_to_json)
    assert callable(format_finding)
    assert callable(render_report)
    assert callable(build_parser)
    assert callable(run)


def test_all_defined():
    import spoke_lint

    assert spoke_lint.__all__ == [
        "Invocation",
        "ArgSpec",
        "Finding",
        "extract_invocations",
        "parse_spoke_args",
        "parse_spoke",
        "canonical_names",
        "diff_invocation",
        "diff_prompt",
        "diff_prompt_full",
        "gate_commands",
        "diff_gate_commands",
        "findings_to_json",
        "format_finding",
        "render_report",
        "build_parser",
        "run",
    ]


def test_exports_are_the_same_objects():
    import spoke_lint
    from spoke_lint.cli import build_parser as _build_parser
    from spoke_lint.cli import run as _run
    from spoke_lint.diff import diff_invocation as _diff_invocation
    from spoke_lint.diff import diff_prompt as _diff_prompt
    from spoke_lint.diff import diff_prompt_full as _diff_prompt_full
    from spoke_lint.extractor import extract_invocations as _extract
    from spoke_lint.gate import diff_gate_commands as _diff_gate
    from spoke_lint.gate import gate_commands as _gate
    from spoke_lint.models import ArgSpec as _ArgSpec
    from spoke_lint.models import Finding as _Finding
    from spoke_lint.models import Invocation as _Invocation
    from spoke_lint.parser import canonical_names as _canonical
    from spoke_lint.parser import parse_spoke as _parse_spoke
    from spoke_lint.parser import parse_spoke_args as _parse
    from spoke_lint.report import findings_to_json as _findings_to_json
    from spoke_lint.report import format_finding as _format_finding
    from spoke_lint.report import render_report as _render_report

    assert spoke_lint.Invocation is _Invocation
    assert spoke_lint.ArgSpec is _ArgSpec
    assert spoke_lint.Finding is _Finding
    assert spoke_lint.extract_invocations is _extract
    assert spoke_lint.parse_spoke_args is _parse
    assert spoke_lint.parse_spoke is _parse_spoke
    assert spoke_lint.canonical_names is _canonical
    assert spoke_lint.diff_invocation is _diff_invocation
    assert spoke_lint.diff_prompt is _diff_prompt
    assert spoke_lint.diff_prompt_full is _diff_prompt_full
    assert spoke_lint.gate_commands is _gate
    assert spoke_lint.diff_gate_commands is _diff_gate
    assert spoke_lint.findings_to_json is _findings_to_json
    assert spoke_lint.format_finding is _format_finding
    assert spoke_lint.render_report is _render_report
    assert spoke_lint.build_parser is _build_parser
    assert spoke_lint.run is _run
