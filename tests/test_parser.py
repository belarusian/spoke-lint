"""Tests for spoke_lint.parser: parse_spoke_args."""

from __future__ import annotations

from pathlib import Path

import pytest

from spoke_lint.models import ArgSpec
from spoke_lint.parser import parse_spoke_args

FIXTURES = Path(__file__).parent / "fixtures"


class TestRequiredFlag:
    def test_required_flag(self):
        result = parse_spoke_args(FIXTURES / "required_flag.py")
        assert len(result) == 1
        spec = result[0]
        assert spec.name == "topic"
        assert spec.required is True
        assert spec.default is None


class TestDefaultInt:
    def test_default_int(self):
        result = parse_spoke_args(FIXTURES / "default_int.py")
        assert len(result) == 1
        spec = result[0]
        assert spec.name == "max-steps"
        assert spec.required is False
        assert spec.default == "150"


class TestDefaultNone:
    def test_default_none(self):
        result = parse_spoke_args(FIXTURES / "default_none.py")
        assert len(result) == 1
        spec = result[0]
        assert spec.name == "briefing"
        assert spec.required is False
        assert spec.default is None


class TestMultiline:
    def test_multiline_call(self):
        result = parse_spoke_args(FIXTURES / "multiline.py")
        assert len(result) == 1
        spec = result[0]
        assert spec.name == "output-dir"
        assert spec.required is False
        assert spec.default == "/tmp/out"


class TestMultiArgsOrder:
    def test_order_preserved(self):
        result = parse_spoke_args(FIXTURES / "multi_args.py")
        assert len(result) == 3
        assert result[0] == ArgSpec(name="alpha", required=True, default=None)
        assert result[1] == ArgSpec(name="beta", required=False, default="42")
        assert result[2] == ArgSpec(name="gamma", required=False, default=None)

    def test_names_in_source_order(self):
        result = parse_spoke_args(FIXTURES / "multi_args.py")
        assert [s.name for s in result] == ["alpha", "beta", "gamma"]


class TestNoArgs:
    def test_no_arg_script_returns_empty(self):
        result = parse_spoke_args(FIXTURES / "no_args.py")
        assert result == []


class TestMissingFile:
    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_spoke_args("/nonexistent/path/to/spoke.py")

    def test_missing_file_message(self):
        with pytest.raises(FileNotFoundError, match="Spoke script not found"):
            parse_spoke_args("/nonexistent/path/to/spoke.py")


class TestReturnType:
    def test_returns_list_of_argspec(self):
        result = parse_spoke_args(FIXTURES / "required_flag.py")
        assert isinstance(result, list)
        assert all(isinstance(s, ArgSpec) for s in result)


class TestPathTypes:
    def test_accepts_str_path(self):
        result = parse_spoke_args(str(FIXTURES / "required_flag.py"))
        assert len(result) == 1
        assert result[0].name == "topic"

    def test_accepts_path_object(self):
        result = parse_spoke_args(FIXTURES / "required_flag.py")
        assert len(result) == 1
        assert result[0].name == "topic"
