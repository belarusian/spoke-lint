# spoke-lint

Static validator for four pipeline runner prompts.

Given a runner prompt file and a spokes directory, `spoke-lint`:

1. Extracts all spoke invocation command lines from the prompt
   (regex for `python3 .../spokes/*.py`).
2. Parses each referenced spoke script to discover its argparse arguments
   (name, required, default).
3. Diffs the two: reports args passed-in-prompt but not-accepted-by-spoke,
   required-spoke-args missing-from-prompt, and gate commands referencing
   tools not in PATH.

## CLI

    spoke-lint check <runner-prompt> --spokes-dir <dir> [--path DIR1,DIR2,...]

`check` is the only subcommand. `--spokes-dir` defaults to `./spokes`; `--path`
optionally overrides the directories used to resolve gate-command tools (defaults
to the current process `PATH`). The report is printed to stdout; errors go to
stderr. Exit code: `0` when clean, `1` when findings exist, `2` on usage/IO error.

Deterministic, stdlib-first, fully tested (pytest + ruff + mypy gate).
