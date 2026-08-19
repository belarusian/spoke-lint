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

    spoke-lint check <runner-prompt> --spokes-dir <dir> [--path DIR1,DIR2,...] [--json]

`check` is the only subcommand. `--spokes-dir` defaults to `./spokes`; `--path`
optionally overrides the directories used to resolve gate-command tools (defaults
to the current process `PATH`). The report is printed to stdout; errors go to
stderr. Exit code: `0` when clean, `1` when findings exist, `2` on usage/IO error.

Pass `--json` to emit a machine-readable JSON array of findings on stdout instead
of the human report (each element has `kind`, `flag`, and `message`). The exit-code
contract is unchanged: `--json` only changes the stdout payload, never the code.

Deterministic, stdlib-first, fully tested (pytest + ruff + mypy gate).

## API

`spoke-lint` is also a library. The stable public surface is `spoke_lint.__all__`;
import from the package root (`from spoke_lint import ...`). The pipeline is layered
so each stage can be used on its own:

| Entry point | Description |
|---|---|
| `extract_invocations(text)` | Extract spoken invocation lines from a prompt as `Invocation` objects, in document order. |
| `parse_spoke_args(path)` | Parse a spoke script's AST and return its argparse arguments as `ArgSpec` objects, in source order. |
| `parse_spoke(path)` | Convenience wrapper returning `{canonical_name: ArgSpec}` for O(1) lookup. |
| `canonical_names(specs)` | The set of canonical accepted argument names from a list of `ArgSpec`. |
| `diff_invocation(invocation, specs)` | Diff one invocation against a spoke's signature; returns `Finding` objects. |
| `diff_prompt(text, spokes_dir, path=None)` | Diff every invocation in a prompt (plus gate commands) against the spokes under `spokes_dir`. |
| `diff_prompt_full(text, spokes_dir, path=None)` | Explicit "lint the whole prompt" entry point; identical to `diff_prompt`. |
| `gate_commands(text)` | Extract the leading executable of each shell gate line, in document order. |
| `diff_gate_commands(text, path=None)` | Flag gate tools not resolvable on `path` as `missing_tool` findings. |
| `render_report(findings)` | Render findings as a deterministic human-readable report (`"OK"` when empty). |
| `findings_to_json(findings)` | Serialize findings to a deterministic JSON array string (`"[]"` when empty). |
| `format_finding(finding)` | Render a single finding as one stable line. |
| `build_parser()` | Build the CLI argument parser (a thin orchestration layer). |
| `run(argv=None)` | Run the CLI in-process and return the exit code (`0`/`1`/`2`). |

The value objects shared across layers are `Invocation`, `ArgSpec`, and `Finding`.

## Development

Install the package in editable mode:

    pip install -e .

Run the test suite:

    pytest tests/ -q

Run the gate (lint + type-check):

    ruff check spoke_lint/ && mypy spoke_lint/ --ignore-missing-imports

The package itself is stdlib-only (`dependencies = []`); `pytest`, `ruff`, and
`mypy` are dev/test tools. Coverage is configured in `pyproject.toml`
(`[tool.coverage.run]` / `[tool.coverage.report]`), so `coverage run -m pytest
tests/ && coverage report` works out of the box.
