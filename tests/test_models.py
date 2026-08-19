"""Tests for spoke_lint.models: Invocation and ArgSpec value objects."""

from __future__ import annotations

import dataclasses

import pytest

from spoke_lint.models import ArgSpec, Invocation


class TestInvocation:
    def test_is_frozen(self):
        inv = Invocation("a.py", (("--goal", "x"),))
        with pytest.raises(dataclasses.FrozenInstanceError):
            inv.script_path = "b.py"  # type: ignore[misc]

    def test_is_hashable(self):
        inv = Invocation("a.py", (("--goal", "x"),))
        # Frozen dataclasses with hashable fields are hashable.
        assert isinstance(hash(inv), int)
        # Equal instances hash equal.
        assert hash(inv) == hash(Invocation("a.py", (("--goal", "x"),)))

    def test_args_is_tuple(self):
        inv = Invocation("a.py", (("--goal", "x"), ("--verbose", None)))
        assert isinstance(inv.args, tuple)
        assert all(isinstance(pair, tuple) for pair in inv.args)

    def test_args_order_preserved(self):
        inv = Invocation("a.py", (("--a", "1"), ("--b", "2"), ("--c", None)))
        assert inv.args == (("--a", "1"), ("--b", "2"), ("--c", None))

    def test_flag_names_strips_dashes_and_preserves_order(self):
        inv = Invocation(
            "a.py",
            (("--goal", "x"), ("-v", None), ("--endpoint", "http://x"), ("--flag", "-y")),
        )
        assert inv.flag_names() == ["goal", "v", "endpoint", "flag"]

    def test_flag_names_empty(self):
        assert Invocation("a.py", ()).flag_names() == []

    def test_bare_flag_value_is_none(self):
        inv = Invocation("a.py", (("--verbose", None),))
        assert inv.args[0] == ("--verbose", None)


class TestArgSpec:
    def test_defaults(self):
        spec = ArgSpec(name="goal")
        assert spec.required is False
        assert spec.default is None

    def test_is_frozen(self):
        spec = ArgSpec(name="goal")
        with pytest.raises(dataclasses.FrozenInstanceError):
            spec.name = "other"  # type: ignore[misc]

    def test_explicit_values(self):
        spec = ArgSpec(name="goal", required=True, default="essay")
        assert spec.required is True
        assert spec.default == "essay"

    def test_is_hashable(self):
        assert isinstance(hash(ArgSpec(name="goal")), int)
