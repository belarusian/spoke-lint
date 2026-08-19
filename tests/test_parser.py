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


class TestPositionalArg:
    def test_positional_required_no_default(self):
        result = parse_spoke_args(FIXTURES / "positional_only.py")
        assert len(result) == 1
        spec = result[0]
        assert spec.name == "topic"
        assert spec.required is True
        assert spec.default is None

    def test_positional_overrides_required_keyword(self):
        # A positional with an explicit required=False must still be required=True.
        import textwrap
        src = textwrap.dedent(
            """
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("topic", required=False, default="x")
            """
        )
        p = FIXTURES / "_tmp_positional_kw.py"
        p.write_text(src, encoding="utf-8")
        try:
            result = parse_spoke_args(p)
            assert result == [ArgSpec(name="topic", required=True, default=None)]
        finally:
            p.unlink()


class TestShortFlag:
    def test_short_flag_name(self):
        result = parse_spoke_args(FIXTURES / "short_flag.py")
        assert len(result) == 1
        spec = result[0]
        assert spec.name == "v"
        assert spec.required is False
        assert spec.default is None


class TestStoreActions:
    def test_store_true(self):
        result = parse_spoke_args(FIXTURES / "store_actions.py")
        by_name = {s.name: s for s in result}
        verbose = by_name["verbose"]
        assert verbose.required is False
        assert verbose.default is None

    def test_count_action(self):
        result = parse_spoke_args(FIXTURES / "store_actions.py")
        by_name = {s.name: s for s in result}
        count = by_name["count"]
        assert count.required is False
        assert count.default is None

    def test_store_false_ignores_default(self):
        # store_false with an explicit default= must still surface default=None.
        import textwrap
        src = textwrap.dedent(
            """
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--enabled", action="store_false", default=True)
            """
        )
        p = FIXTURES / "_tmp_store_false.py"
        p.write_text(src, encoding="utf-8")
        try:
            result = parse_spoke_args(p)
            assert result == [ArgSpec(name="enabled", required=False, default=None)]
        finally:
            p.unlink()


class TestParseSpokeDict:
    def test_returns_dict_keyed_by_canonical_name(self):
        from spoke_lint.parser import parse_spoke

        result = parse_spoke(FIXTURES / "multi_args.py")
        assert isinstance(result, dict)
        assert set(result.keys()) == {"alpha", "beta", "gamma"}
        assert all(isinstance(v, ArgSpec) for v in result.values())
        assert result["alpha"] == ArgSpec(name="alpha", required=True, default=None)
        assert result["beta"] == ArgSpec(name="beta", required=False, default="42")

    def test_last_wins_on_duplicate(self):
        import textwrap

        from spoke_lint.parser import parse_spoke
        src = textwrap.dedent(
            """
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--dup", required=True)
            parser.add_argument("--dup", default="later")
            """
        )
        p = FIXTURES / "_tmp_dup.py"
        p.write_text(src, encoding="utf-8")
        try:
            result = parse_spoke(p)
            assert set(result.keys()) == {"dup"}
            # The later add_argument (default="later", not required) wins.
            assert result["dup"] == ArgSpec(name="dup", required=False, default="later")
        finally:
            p.unlink()

    def test_missing_file_raises(self):
        from spoke_lint.parser import parse_spoke

        with pytest.raises(FileNotFoundError, match="Spoke script not found"):
            parse_spoke("/nonexistent/path/to/spoke.py")

    def test_accepts_str_and_path(self):
        from spoke_lint.parser import parse_spoke

        as_str = parse_spoke(str(FIXTURES / "short_flag.py"))
        as_path = parse_spoke(FIXTURES / "short_flag.py")
        assert as_str == as_path
        assert set(as_str.keys()) == {"v"}
