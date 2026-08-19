# TICKET-028 — cli.run + main: orchestration and exit-code contract

**Cycle:** 8 (CLI phase, Build Order phase 7)
**Module:** `spoke_lint/cli.py` (new)

## Capability
The thin orchestration layer that ties the diffing/reporting modules to a process
exit code. All semantics live in `diff.py`/`report.py`; this module only reads the
file, calls the pipeline, prints, and returns a code.

### run(argv: list[str] | None = None) -> int
- Parse args via `build_parser` (defaulting to `sys.argv[1:]` when `argv is None`).
- Read the prompt file text (`Path(prompt_file).read_text()`).
- Split `--path` on commas into a `list[str]` (or `None` when the option was not
  given) and pass it as `path` to `diff_prompt_full`.
- Call `diff_prompt_full(text, Path(spokes_dir), path)` → findings.
- Render with `render_report(findings)` and print to **stdout**.
- Return an **exit code**:
  - `0` when there are no findings (report is `"OK"`).
  - `1` when one or more findings exist.
  - `2` when the prompt file is missing/unreadable — write a distinct error message
    to **stderr** and do NOT raise.

### main() -> None
- Thin wrapper: `sys.exit(run())`. Guarded under `if __name__ == "__main__":`.

## Rules
- stdlib-only (`argparse`, `sys`, `pathlib`). No subprocesses.
- Pure orchestration: no diffing/reporting logic duplicated here.
- The exit-code contract (0 = clean, 1 = findings, 2 = usage/IO error) is the
  load-bearing guarantee for later automation.

## Acceptance
- Valid prompt file → returns `0`, stdout `"OK"`.
- Prompt with an unknown flag / missing required arg → returns `1`, multi-line report
  on stdout.
- Referenced-but-missing script → returns `1` with a `missing_script` line.
- Gate tool absent from `--path` → returns `1` with a `missing_tool` line.
- Non-existent prompt file → returns `2`, error on stderr, no exception raised.
