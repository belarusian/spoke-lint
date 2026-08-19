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


class TestMultiOption:
    def test_multi_option_emits_long_canonical_name(self):
        result = parse_spoke_args(FIXTURES / "multi_option.py")
        assert len(result) == 1
        spec = result[0]
        assert spec.name == "verbose"
        assert spec.required is False
        assert spec.default is None

    def test_multi_option_long_name_not_short(self):
        result = parse_spoke_args(FIXTURES / "multi_option.py")
        assert result[0].name != "v"

    def test_only_short_options_keep_strip_dashes(self):
        # Only short options present: first short option wins, dashes stripped.
        import textwrap

        src = textwrap.dedent(
            """
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("-a", "-b", help="two shorts")
            """
        )
        p = FIXTURES / "_tmp_two_shorts.py"
        p.write_text(src, encoding="utf-8")
        try:
            result = parse_spoke_args(p)
            assert result == [ArgSpec(name="a", required=False, default=None)]
        finally:
            p.unlink()

    def test_long_option_preferred_over_short(self):
        import textwrap

        src = textwrap.dedent(
            """
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("-x", "--extra", required=True)
            """
        )
        p = FIXTURES / "_tmp_long_pref.py"
        p.write_text(src, encoding="utf-8")
        try:
            result = parse_spoke_args(p)
            assert result == [ArgSpec(name="extra", required=True, default=None)]
        finally:
            p.unlink()


class TestNargs:
    def test_positional_nargs_plus_required(self):
        result = parse_spoke_args(FIXTURES / "nargs_spoke.py")
        by_name = {s.name: s for s in result}
        assert by_name["inputs"].required is True
        assert by_name["inputs"].default is None

    def test_positional_nargs_question_not_required(self):
        result = parse_spoke_args(FIXTURES / "nargs_spoke.py")
        by_name = {s.name: s for s in result}
        assert by_name["config"].required is False
        assert by_name["config"].default is None

    def test_dashed_flag_nargs_star_not_required(self):
        result = parse_spoke_args(FIXTURES / "nargs_spoke.py")
        by_name = {s.name: s for s in result}
        assert by_name["tags"].required is False
        assert by_name["tags"].default is None

    def test_positional_nargs_int_required(self):
        import textwrap

        src = textwrap.dedent(
            """
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("pair", nargs=2)
            """
        )
        p = FIXTURES / "_tmp_nargs_int.py"
        p.write_text(src, encoding="utf-8")
        try:
            result = parse_spoke_args(p)
            assert result == [ArgSpec(name="pair", required=True, default=None)]
        finally:
            p.unlink()

    def test_dashed_flag_nargs_plus_keeps_required_handling(self):
        # A dashed flag with nargs="+" keeps existing required/default handling.
        import textwrap

        src = textwrap.dedent(
            """
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--files", nargs="+", required=True)
            """
        )
        p = FIXTURES / "_tmp_flag_nargs_plus.py"
        p.write_text(src, encoding="utf-8")
        try:
            result = parse_spoke_args(p)
            assert result == [ArgSpec(name="files", required=True, default=None)]
        finally:
            p.unlink()

    def test_dashed_flag_nargs_star_with_default(self):
        import textwrap

        src = textwrap.dedent(
            """
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--opts", nargs="*", default="none")
            """
        )
        p = FIXTURES / "_tmp_flag_nargs_star_default.py"
        p.write_text(src, encoding="utf-8")
        try:
            result = parse_spoke_args(p)
            assert result == [ArgSpec(name="opts", required=False, default="none")]
        finally:
            p.unlink()


class TestSubparsers:
    def test_subparser_args_collected(self):
        result = parse_spoke_args(FIXTURES / "subparser_spoke.py")
        by_name = {s.name: s for s in result}
        assert set(by_name.keys()) == {"epochs", "metric"}

    def test_subparser_arg_names_prefix_free(self):
        result = parse_spoke_args(FIXTURES / "subparser_spoke.py")
        by_name = {s.name: s for s in result}
        assert by_name["epochs"].required is False
        assert by_name["epochs"].default == "10"
        assert by_name["metric"].required is True
        assert by_name["metric"].default is None

    def test_subparser_args_interleaved_by_line(self):
        # Sub-parser args appear in source order relative to top-level args.
        import textwrap

        src = textwrap.dedent(
            """
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument("--top", required=True)
            sub = parser.add_subparsers()
            cmd = sub.add_parser("go")
            cmd.add_argument("--flag", default="x")
            """
        )
        p = FIXTURES / "_tmp_sub_interleave.py"
        p.write_text(src, encoding="utf-8")
        try:
            result = parse_spoke_args(p)
            assert [s.name for s in result] == ["top", "flag"]
        finally:
            p.unlink()


class TestCanonicalNames:
    def test_returns_set_of_names(self):
        from spoke_lint.parser import canonical_names

        specs = [ArgSpec(name="a"), ArgSpec(name="b")]
        assert canonical_names(specs) == {"a", "b"}

    def test_empty_list_empty_set(self):
        from spoke_lint.parser import canonical_names

        assert canonical_names([]) == set()

    def test_deduplicates_names(self):
        from spoke_lint.parser import canonical_names

        specs = [ArgSpec(name="a"), ArgSpec(name="a"), ArgSpec(name="b")]
        assert canonical_names(specs) == {"a", "b"}
