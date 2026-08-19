# TICKET-025 — tests/test_report.py: deterministic report renderer tests

**Cycle:** 7 (Reporting phase, Build Order phase 6)
**Module:** `tests/test_report.py` (new)

## Capability
Deterministic unit tests for `spoke_lint.report.format_finding` and
`render_report`. No I/O, no PATH dependence.

## Tests (minimum)
- `format_finding` returns the exact `<kind>: <flag> — <message>` line; stable across
  repeated calls (byte-equal).
- `render_report([])` == `"OK"`.
- A single finding → one line equal to `format_finding(f)`.
- Multiple findings of the SAME kind preserve input order.
- Mixed kinds group in `_KIND_ORDER` (missing_script, unknown_flag, missing_required,
  missing_tool); assert exact expected multi-line string.
- An unknown kind is appended after known groups, sorted by name (determinism).
- `render_report` output is deterministic: two calls on the same list are byte-equal.
- Every line emitted by `render_report` equals `format_finding` of some input finding
  (line/finding correspondence).

## Acceptance
- All tests pass under `pytest tests/ -x -q`.
- No host-PATH or filesystem dependence (pure string assertions on constructed
  Finding objects).
