# TICKET-038 — export findings_to_json + document --json in README

**Cycle:** 10 (CLI phase, Build Order phase 7)
**Modules:** `spoke_lint/__init__.py`, `tests/test_package.py`, `README.md`

## Capability
Make the new serializer part of the public API and document the new CLI flag.

### spoke_lint/__init__.py
- Export `findings_to_json` alongside the existing API; `__all__` grows to 17
  entries.

### tests/test_package.py
- Update for the new `__all__`: import + callable assertion, exact `__all__` list,
  and an identity assertion (`spoke_lint.findings_to_json is report.findings_to_json`).

### README.md
- Document the `--json` flag in the CLI section:
  `spoke-lint check <runner-prompt> --spokes-dir <dir> [--path ...] [--json]`.
- Note that `--json` emits a JSON array of findings (machine-readable) instead of
  the human report, and that the exit-code contract is unchanged.

## Rules
- Keep `__all__` changes deliberate; update `test_package.py` to match exactly.
- README must match the implemented flag exactly.

## Acceptance
- `spoke_lint.__all__` has 17 entries including `findings_to_json`.
- `test_package.py` passes with the new export.
- README documents `--json` and its effect on stdout.
