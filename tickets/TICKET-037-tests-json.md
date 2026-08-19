# TICKET-037 — tests for findings_to_json and the --json CLI flag

**Cycle:** 10 (CLI phase, Build Order phase 7)
**Modules:** `tests/test_report.py`, `tests/test_cli.py`

## Capability
Deterministic, hermetic coverage for the new JSON output mode.

### tests/test_report.py — findings_to_json
- Empty list → `"[]"`.
- A single finding → a one-element array with exact `kind`/`flag`/`message` keys
  (assert via `json.loads`).
- Multiple findings preserve input order in the emitted array.
- Output is valid JSON: `json.loads` round-trips to the same field values.
- Byte-determinism across calls.

### tests/test_cli.py — `--json` flag (hermetic, capsys + json.loads)
- A clean prompt + `--json` → exit 0 and stdout `"[]"`.
- A prompt with an unknown flag + `--json` → exit 1 and stdout is valid JSON whose
  first element has the expected `kind`/`flag`/`message`.
- A missing prompt file + `--json` → exit 2 with a stderr error (no exception,
  empty stdout).
- Keep all existing Cycle 9 tests green.

## Rules
- No subprocesses; in-process `run([...])` calls with `capsys`.
- Do not delete or weaken any existing coverage.

## Acceptance
- All new tests pass and the full suite stays green (no regression from 147).
