"""Tests for spoke_lint package-level public API (TICKET-004, 007, 010, 014, 018)."""

from __future__ import annotations


def test_public_api_importable():
    from spoke_lint import (
        ArgSpec,
        Finding,
        Invocation,
        canonical_names,
        diff_gate_commands,
        diff_invocation,
        diff_prompt,
        extract_invocations,
        gate_commands,
        parse_spoke,
        parse_spoke_args,
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
    assert callable(gate_commands)
    assert callable(diff_gate_commands)


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
        "gate_commands",
        "diff_gate_commands",
    ]


def test_exports_are_the_same_objects():
    import spoke_lint
    from spoke_lint.diff import diff_invocation as _diff_invocation
    from spoke_lint.diff import diff_prompt as _diff_prompt
    from spoke_lint.extractor import extract_invocations as _extract
    from spoke_lint.gate import diff_gate_commands as _diff_gate
    from spoke_lint.gate import gate_commands as _gate
    from spoke_lint.models import ArgSpec as _ArgSpec
    from spoke_lint.models import Finding as _Finding
    from spoke_lint.models import Invocation as _Invocation
    from spoke_lint.parser import canonical_names as _canonical
    from spoke_lint.parser import parse_spoke as _parse_spoke
    from spoke_lint.parser import parse_spoke_args as _parse

    assert spoke_lint.Invocation is _Invocation
    assert spoke_lint.ArgSpec is _ArgSpec
    assert spoke_lint.Finding is _Finding
    assert spoke_lint.extract_invocations is _extract
    assert spoke_lint.parse_spoke_args is _parse
    assert spoke_lint.parse_spoke is _parse_spoke
    assert spoke_lint.canonical_names is _canonical
    assert spoke_lint.diff_invocation is _diff_invocation
    assert spoke_lint.diff_prompt is _diff_prompt
    assert spoke_lint.gate_commands is _gate
    assert spoke_lint.diff_gate_commands is _diff_gate
