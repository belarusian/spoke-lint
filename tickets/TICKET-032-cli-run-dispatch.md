# TICKET-032 — cli.run: dispatch on subcommand, preserve exit-code contract

**Cycle:** 9 (CLI phase, Build Order phase 7)
**Module:** `spoke_lint/cli.py`

## Capability
Keep `run(argv=None) -> int` as the single entry point. It must now **dispatch on
the subcommand** and preserve the exact exit-code contract from Cycle 8.

### run(argv: list[str] | None = None) -> int
- Parse via `build_parser()`.
- Dispatch on `args.command`; only `check` is implemented (current behavior).
- Preserve the report printed to stdout and errors on stderr exactly as in Cycle 8;
  do not change the rendered report format (it comes from `render_report`).

## Exit-code contract (load-bearing)
- `0` — no findings (rendered report is `"OK"`).
- `1` — one or more findings were produced.
- `2` — usage / I/O error (prompt file missing/unreadable, **or** a missing /
  unrecognized subcommand). An error message goes to stderr; **no exception escapes
  `run`**.

## Rules
- A missing or unrecognized subcommand must return a non-zero code (typically `2`)
  rather than raising. Catch `argparse.ArgumentError`/`SystemExit` from
  `parse_args` and translate to a returned code with a stderr message.
- The refactor must be behavior-preserving for the existing `check` semantics.
- stdlib-only; all diffing/reporting semantics stay in `diff.py`/`report.py`.

## Acceptance
- `run(["check", <prompt>, "--spokes-dir", ...])` → 0 / `"OK"` when clean.
- Findings → 1 with the expected report lines.
- Missing prompt file → 2 + stderr error, no exception.
- `run([])` or `run(["bogus"])` → non-zero (typically 2), no traceback.
