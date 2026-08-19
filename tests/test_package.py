"""Tests for spoke_lint package-level public API (TICKET-004)."""

from __future__ import annotations


def test_public_api_importable():
    from spoke_lint import ArgSpec, Invocation, extract_invocations

    assert Invocation is not None
    assert ArgSpec is not None
    assert callable(extract_invocations)


def test_all_defined():
    import spoke_lint

    assert spoke_lint.__all__ == ["Invocation", "ArgSpec", "extract_invocations"]


def test_exports_are_the_same_objects():
    import spoke_lint
    from spoke_lint.extractor import extract_invocations as _extract
    from spoke_lint.models import ArgSpec as _ArgSpec
    from spoke_lint.models import Invocation as _Invocation

    assert spoke_lint.Invocation is _Invocation
    assert spoke_lint.ArgSpec is _ArgSpec
    assert spoke_lint.extract_invocations is _extract
