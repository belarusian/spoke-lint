# TICKET-030 — console-script entry point + package export

**Cycle:** 8 (CLI phase, Build Order phase 7)
**Module:** `pyproject.toml`, `spoke_lint/__init__.py`, `tests/test_package.py`

## Capability
Make the CLI installable and invocable as `spoke-lint <prompt>`, and decide whether
to expose the CLI functions in the public API.

## Rules
- `pyproject.toml`: ensure a console-script entry point
  `spoke-lint = "spoke_lint.cli:main"` under `[project.scripts]`. (Already present —
  verify it matches the real `spoke_lint.cli:main`.) Keep it minimal; no non-stdlib
  dependencies.
- `spoke_lint/__init__.py`: optionally export a stable `run`/`build_parser` if they
  are to be part of the public API. Keep `__all__` changes deliberate. If exported,
  update `tests/test_package.py` (import + callable assert, exact `__all__`, identity).

## Acceptance
- `spoke-lint` entry point resolves to `spoke_lint.cli:main`.
- `tests/test_package.py` green under `pytest tests/ -x -q`.
