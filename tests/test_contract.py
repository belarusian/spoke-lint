"""Tests for spoke_lint.contract: is_runner_prompt (Cycle 15, issue #60).

The input contract is a runner prompt (markdown + bash blocks). Pure shell
launch scripts are rejected so the CLI exits 2 with one diagnostic instead of a
``missing_tool`` flood. All tests are hermetic and deterministic.
"""

from __future__ import annotations

from pathlib import Path

from spoke_lint.contract import is_runner_prompt

FIXTURES = Path(__file__).parent / "fixtures"


class TestRunnerPromptAccepted:
    def test_plain_prose_is_a_runner_prompt(self):
        assert is_runner_prompt("Now run the full pipeline\n") is True

    def test_prose_with_invocation_is_a_runner_prompt(self):
        text = "Run it\npython3 /a/spokes/no_args.py\n"
        assert is_runner_prompt(text) is True

    def test_prose_with_gate_commands_is_a_runner_prompt(self):
        text = "Gate first\npytest tests/ -x -q\nruff check spoke_lint/\n"
        assert is_runner_prompt(text) is True

    def test_fenced_shell_block_is_still_a_runner_prompt(self):
        # Shell statements inside a fenced block are ignored; the outside
        # content is prose -> a runner prompt.
        fence = chr(96) * 3
        text = (
            "Run the gate:\n"
            + fence + "\n"
            + "set -uo pipefail\n"
            + "export FIVE_MODEL=x\n"
            + "pytest tests/ -x -q\n"
            + fence + "\n"
            + "Then report.\n"
        )
        assert is_runner_prompt(text) is True

    def test_empty_text_is_a_runner_prompt(self):
        assert is_runner_prompt("") is True


class TestShellRejected:
    def test_shebang_rejected(self):
        assert is_runner_prompt("#!/bin/bash\necho hi\n") is False

    def test_heredoc_rejected(self):
        assert is_runner_prompt("INNER=$(cat <<'EOF'\nhello\nEOF\n)\n") is False

    def test_two_shell_statements_rejected(self):
        text = "export FIVE_MODEL=x\nexport FIVE_BASE_URL=y\n"
        assert is_runner_prompt(text) is False

    def test_set_flag_rejected(self):
        text = "set -uo pipefail\nexport FIVE_MODEL=x\n"
        assert is_runner_prompt(text) is False

    def test_assignment_plus_export_rejected(self):
        text = "REG_DIR=\"$HOME/.four/launches\"\nexport FIVE_MODEL=x\n"
        assert is_runner_prompt(text) is False

    def test_single_shell_statement_not_enough(self):
        # One shell statement alone is not conclusive; treat as a prompt.
        assert is_runner_prompt("export FIVE_MODEL=x\n") is True


class TestLaunchSetupFixture:
    def test_launch_setup_fixture_is_not_a_runner_prompt(self):
        text = (FIXTURES / "launch_setup.sh").read_text(encoding="utf-8")
        assert is_runner_prompt(text) is False
