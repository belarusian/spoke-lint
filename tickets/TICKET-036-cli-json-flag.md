# TICKET-036 — cli: `--json` flag on the `check` subcommand

**Cycle:** 10 (CLI phase, Build Order phase 7)
**Module:** `spoke_lint/cli.py`

## Capability
Add a `--json` machine-readable output mode to the existing `check` subcommand so
downstream automation can consume findings as structured JSON rather than parsing
the human report. The exit-code contract (0/1/2) is unchanged; only the stdout
payload changes.

### build_parser()
- Add a `--json` flag to the `check` subcommand: `action="store_true"`, default
  `False`. No side effects in `build_parser`.

### _run_check(args) / run(argv)
- When `args.json` is set, print `findings_to_json(findings)` to stdout **instead
  of** `render_report(findings)`.
- Exit-code contract unchanged: `0` when no findings (print `[]`), `1` when
  findings exist, `2` on usage/IO error.
- When `--json` is absent, behavior is byte-identical to Cycle 9 (human report).

## Rules
- stdlib-only (`argparse`, `sys`, `pathlib`). JSON serialization lives in
  `report.py`; the CLI stays a thin orchestration layer.
- No exception escapes for a missing/unreadable prompt file even with `--json`.

## Acceptance
- `build_parser().parse_args(["check", "p.txt", "--json"])` yields `json=True`.
- A clean prompt + `--json` → exit 0, stdout `"[]"`.
- A prompt with findings + `--json` → exit 1, stdout is valid JSON.
- A missing prompt file + `--json` → exit 2, stderr error, empty stdout.
