# TICKET-003 — Tests for models + extractor

**Phase:** Extraction (Cycle 1)
**Module:** `tests/test_models.py`, `tests/test_extractor.py`
**Status:** open

## What
Cover the two Cycle-1 modules with deterministic, stdlib-only tests.

### test_models.py
- `Invocation` is frozen (mutating raises), hashable, `.args` is a tuple.
- `Invocation.flag_names()` strips dashes and preserves order.
- `ArgSpec` defaults: `required=False`, `default=None`.

### test_extractor.py
- Single clean invocation line → correct script_path + ordered args.
- Indented (4-space) lines are detected.
- `python` (no 3) and env-var-prefixed (`FIVE_MODEL=x python ...`) lines are detected.
- Bare flag yields `value=None`.
- A value that itself starts with `-` is NOT swallowed as a flag (e.g. `--flag -x`).
- Prose / non-spoke lines are ignored; multiple invocations return in document order.
- Empty input → empty list.

## Acceptance
All tests pass under `pytest tests/ -x -q`. No network, no LLM, deterministic.
