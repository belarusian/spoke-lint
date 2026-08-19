# TICKET-031 — cli.build_parser: `check` subcommand interface

**Cycle:** 9 (CLI phase, Build Order phase 7)
**Module:** `spoke_lint/cli.py`

## Capability
Refactor `build_parser()` to a **subcommand** interface so the installed
`spoke-lint check <prompt> --spokes-dir <dir>` invocation documented in the README
actually works. The parser must expose one subcommand, `check`, that carries the
current behavior.

### build_parser() -> argparse.ArgumentParser
- One subcommand: `check`.
- `check` positional `prompt_file`: path to the runner prompt text file.
- `check` option `--spokes-dir` (default `"./spokes"`): directory containing the
  referenced spoke scripts.
- `check` option `--path` (optional, default `None`): a **comma-separated** list of
  directories used to resolve gate-command executables. When omitted, the current
  process `PATH` is used downstream.

## Rules
- stdlib-only (`argparse`). No I/O, no side effects in `build_parser`.
- The subcommand must be required: a call with **no** subcommand (or an unrecognized
  one) must produce a non-zero exit code (argparse's default `2` is acceptable)
  rather than raising an unhandled exception out of `run`.
- `--path` remains the raw comma-separated string; splitting stays in `run`.

## Acceptance
- `build_parser()` returns an `argparse.ArgumentParser`.
- Parsing `["check", "prompt.txt"]` yields `command="check"`,
  `prompt_file="prompt.txt"`, `spokes_dir="./spokes"`, `path=None`.
- Parsing `["check", "p.txt", "--spokes-dir", "D", "--path", "a,b"]` yields those.
