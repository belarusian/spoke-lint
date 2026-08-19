# TICKET-029 — tests/test_cli.py: hermetic CLI tests

**Cycle:** 8 (CLI phase, Build Order phase 7)
**Module:** `tests/test_cli.py` (new)

## Capability
Deterministic tests for the CLI using `tmp_path` fixtures and `capsys`. No
subprocesses; call `run([...])` directly.

## Cases
- Valid prompt file → exit `0`, stdout `"OK"`.
- Prompt with an unknown flag / missing required arg → exit `1`, expected multi-line
  report on stdout (assert the exact lines from `render_report`).
- Referenced-but-missing script → exit `1` with a `missing_script` line.
- Gate tool absent from `--path` → exit `1` with a `missing_tool` line. Use
  `monkeypatch.setenv("PATH", ...)` + a temp dir fake executable so the test is
  hermetic (no host-PATH dependence).
- Non-existent prompt file → exit `2`, error on stderr, no exception.

## Rules
- stdlib-only; reuse existing fixtures under `tests/fixtures/` for spoke scripts by
  pointing `--spokes-dir` at that directory.
- Capture stdout/stderr with `capsys`.
- Hermetic: never depend on the host's real PATH for the gate-tool case.

## Acceptance
- All cases green under `pytest tests/ -x -q`.
- Exit codes match the contract exactly (0/1/2).
