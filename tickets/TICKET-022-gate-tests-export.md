# TICKET-022 — tests for gate module + package export

**Cycle:** 6 (Diffing phase, Build Order phase 5)
**Modules:** `tests/test_gate.py` (new), `spoke_lint/__init__.py`, `tests/test_package.py`

## Capability
Deterministic tests for the gate module and updated public API.

### tests/test_gate.py
- A gate line's executable is extracted (`pytest`/`ruff`/`mypy`).
- Env-var prefixes are skipped (`FOO=bar ruff ...` → `ruff`).
- python/spoke invocation lines are NOT treated as gate commands.
- Comment/blank lines skipped.
- A tool present on a hermetic PATH (temp dir + fake executable via
  `monkeypatch.setenv("PATH", ...)`) yields no finding.
- A tool absent from PATH yields a `missing_tool` finding.
- `diff_prompt` appends gate findings after invocation findings; two-arg call still works.

### spoke_lint/__init__.py
- Export `gate_commands`, `diff_gate_commands`; update `__all__`.

### tests/test_package.py
- Update the expected `__all__` list and import/identity assertions for the new exports.

## Acceptance
- All existing 87 tests stay green; new gate tests pass hermetically (no host PATH dependence).
