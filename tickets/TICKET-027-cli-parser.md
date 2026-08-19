# TICKET-027 — cli.build_parser: argparse parser for the spoke-lint CLI

**Cycle:** 8 (CLI phase, Build Order phase 7)
**Module:** `spoke_lint/cli.py` (new)

## Capability
A pure function that builds and returns an `argparse.ArgumentParser` with no side
effects. The parser is the first user-facing surface of spoke-lint.

### build_parser() -> argparse.ArgumentParser
- Positional `prompt_file`: path to the runner prompt text file.
- Option `--spokes-dir` (default `"./spokes"`): directory containing the referenced
  spoke scripts.
- Option `--path` (optional, default `None`): a **comma-separated** list of
  directories used to resolve gate-command executables. When omitted, the current
  process `PATH` is used downstream.

## Rules
- stdlib-only (`argparse`). No I/O, no side effects in `build_parser`.
- The parser must be constructible and parseable in isolation (testable without a
  prompt file on disk).
- `--path` is stored as the raw comma-separated string; splitting happens in
  `run`, not here.

## Acceptance
- `build_parser()` returns an `argparse.ArgumentParser`.
- Parsing `["prompt.txt"]` yields `prompt_file="prompt.txt"`,
  `spokes_dir="./spokes"`, `path=None`.
- Parsing with `--spokes-dir D --path a,b` yields those values.
