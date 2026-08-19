# TICKET-033 — tests/test_cli.py: update/extend hermetic tests for the subcommand form

**Cycle:** 9 (CLI phase, Build Order phase 7)
**Module:** `tests/test_cli.py`

## Capability
Update/extend the existing hermetic CLI tests to the **subcommand argv shape**
(`run(["check", <prompt>, ...])`) rather than deleting coverage. Keep them in-process
(no subprocesses), using `tmp_path` + `capsys`.

## Cases (argv now prefixed with `"check"`)
- Valid prompt file → exit `0`, stdout `"OK"`.
- Unknown flag / missing required arg → exit `1`, expected report lines from
  `render_report`.
- Referenced-but-missing script → exit `1` with a `missing_script` line.
- Gate tool absent from `--path` → exit `1` with a `missing_tool` line (temp-dir fake
  executable / empty dir; hermetic, no host-PATH dependence).
- Present tool via temp fake exe on `--path` → clean (`0`, `"OK"`).
- Non-existent prompt file → exit `2` + stderr error, no exception.
- **New:** a call with **no subcommand** (`run([])`) or an unknown subcommand
  (`run(["bogus", ...])`) → non-zero code (assert `!= 0`, typically `2`) and **no
  traceback**.
- Keep the existing `main()` `SystemExit` test working under the new argv shape.

## Rules
- stdlib-only; reuse `tests/fixtures/` for spoke scripts via `--spokes-dir`.
- Capture stdout/stderr with `capsys`. Hermetic gate-tool cases.

## Acceptance
- All cases green under `pytest tests/ -x -q`; do not regress the 144 passing tests
  from Cycle 8 (update them for the subcommand argv shape).
