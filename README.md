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

    spoke-lint check <runner-prompt> --spokes-dir <dir>

Deterministic, stdlib-first, fully tested (pytest + ruff + mypy gate).
