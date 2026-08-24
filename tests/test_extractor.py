"""Tests for spoke_lint.extractor: extract_invocations."""

from __future__ import annotations

from spoke_lint.extractor import extract_invocations


class TestBasicExtraction:
    def test_single_clean_invocation(self):
        text = 'python3 ~/Research/four/examples/spokes/essay-pipeline.py --topic "X" --endpoint http://x'
        result = extract_invocations(text)
        assert len(result) == 1
        inv = result[0]
        assert inv.script_path == "~/Research/four/examples/spokes/essay-pipeline.py"
        assert inv.args == (("--topic", "X"), ("--endpoint", "http://x"))

    def test_indented_line_detected(self):
        text = "    python3 /a/spokes/b.py --goal g"
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/b.py"
        assert result[0].args == (("--goal", "g"),)

    def test_python_without_three(self):
        text = "python /a/spokes/b.py --goal g"
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/b.py"

    def test_env_var_prefix(self):
        text = "FIVE_MODEL=x python /a/spokes/b.py --goal g"
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/b.py"
        assert result[0].args == (("--goal", "g"),)

    def test_multiple_env_var_prefixes(self):
        text = "A=1 B=2 python3 /a/spokes/b.py --goal g"
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/b.py"


class TestFlagParsing:
    def test_bare_flag_value_none(self):
        text = "python3 /a/spokes/b.py --verbose"
        result = extract_invocations(text)
        assert result[0].args == (("--verbose", None),)

    def test_value_starting_with_dash_not_swallowed(self):
        text = "python3 /a/spokes/b.py --flag -x"
        result = extract_invocations(text)
        assert result[0].args == (("--flag", "-x"),)

    def test_bare_flag_followed_by_flag(self):
        text = "python3 /a/spokes/b.py --verbose --goal x"
        result = extract_invocations(text)
        assert result[0].args == (("--verbose", None), ("--goal", "x"))

    def test_multiple_args_ordered(self):
        text = "python3 /a/spokes/b.py --a 1 --b 2 --c 3"
        result = extract_invocations(text)
        assert result[0].args == (("--a", "1"), ("--b", "2"), ("--c", "3"))

    def test_no_args(self):
        text = "python3 /a/spokes/b.py"
        result = extract_invocations(text)
        assert result[0].args == ()


class TestNonInvocationLines:
    def test_prose_ignored(self):
        text = "Run the essay pipeline now.\npython3 /a/spokes/b.py --goal g"
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/b.py"

    def test_other_commands_ignored(self):
        text = "ls -la\ngit status\npython3 /a/spokes/b.py --goal g"
        result = extract_invocations(text)
        assert len(result) == 1

    def test_non_spoke_python_ignored(self):
        # A .py path without a /spokes/ segment is not a spoke invocation.
        text = "python3 /a/tools/helper.py --goal g"
        result = extract_invocations(text)
        assert result == []

    def test_multiple_invocations_document_order(self):
        text = (
            "python3 /a/spokes/one.py --a 1\n"
            "some prose here\n"
            "python3 /a/spokes/two.py --b 2\n"
        )
        result = extract_invocations(text)
        assert len(result) == 2
        assert result[0].script_path == "/a/spokes/one.py"
        assert result[1].script_path == "/a/spokes/two.py"


class TestEdgeCases:
    def test_empty_input(self):
        assert extract_invocations("") == []

    def test_whitespace_only(self):
        assert extract_invocations("   \n  \n") == []

    def test_absolute_python_path(self):
        text = "/usr/bin/python3 /a/spokes/b.py --goal g"
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/b.py"

    def test_quoted_value_with_spaces(self):
        text = 'python3 /a/spokes/b.py --topic "hello world"'
        result = extract_invocations(text)
        assert result[0].args == (("--topic", "hello world"),)


class TestFencedCodeBlocks:
    """Markdown-awareness: lines inside fenced code blocks are ignored."""

    def test_invocation_inside_fence_not_extracted(self):
        text = (
            "```\n"
            "python3 /a/spokes/ghost.py --x y\n"
            "```\n"
        )
        assert extract_invocations(text) == []

    def test_invocation_outside_fence_extracted(self):
        # Regression guard: a real invocation outside any code block is found.
        text = "python3 /a/spokes/real.py --goal g"
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/real.py"

    def test_non_spoke_snippet_in_fence_then_real_outside(self):
        # A fenced block with a non-spoke python snippet, then a real spoke
        # invocation outside the block -> only the real one is extracted.
        text = (
            "```\n"
            "python3 /a/tools/helper.py --goal g\n"
            "```\n"
            "python3 /a/spokes/real.py --goal g\n"
        )
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/real.py"

    def test_fence_delimiter_lines_never_invocations(self):
        # The fence delimiter lines themselves are never treated as invocations.
        text = (
            "```\n"
            "```\n"
            "python3 /a/spokes/real.py --goal g\n"
        )
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/real.py"

    def test_unclosed_fence_ignores_rest(self):
        # An opening fence with no closing fence -> everything after is ignored.
        text = (
            "python3 /a/spokes/real.py --goal g\n"
            "```\n"
            "python3 /a/spokes/ghost.py --x y\n"
        )
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/real.py"

    def test_language_tagged_fence_same_as_bare(self):
        # A fenced block with a language tag is handled the same as a bare fence.
        text = (
            "```python\n"
            "python3 /a/spokes/ghost.py --x y\n"
            "```\n"
            "python3 /a/spokes/real.py --goal g\n"
        )
        result = extract_invocations(text)
        assert len(result) == 1
        assert result[0].script_path == "/a/spokes/real.py"
