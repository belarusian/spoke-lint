# TICKET-026 — package exports: diff_prompt_full, render_report, format_finding

**Cycle:** 7 (Reporting phase, Build Order phase 6)
**Module:** `spoke_lint/__init__.py`, `tests/test_package.py`

## Capability
Export the new public API alongside the existing 11 entries and update the package
test to assert the new `__all__`.

## Rules
- Add imports: `from spoke_lint.diff import diff_prompt_full`;
  `from spoke_lint.report import format_finding, render_report`.
- Extend `__all__` (now 14 entries) with `"diff_prompt_full"`, `"render_report"`,
  `"format_finding"` in a stable position (group by module: after the diff exports,
  then report exports).
- Update `tests/test_package.py`:
  - `test_public_api_importable` imports + asserts callable for the three new names.
  - `test_all_defined` asserts the exact new 14-entry `__all__`.
  - `test_exports_are_the_same_objects` asserts identity with the module-level objects.

## Acceptance
- `import spoke_lint; spoke_lint.diff_prompt_full is diff.diff_prompt_full`, etc.
- `tests/test_package.py` green under `pytest tests/ -x -q`.
