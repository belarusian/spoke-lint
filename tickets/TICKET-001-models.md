# TICKET-001 — Shared dataclasses: Invocation + ArgSpec

**Phase:** Extraction (Cycle 1)
**Module:** `spoke_lint/models.py`
**Status:** open

## What
Define the two shared value objects every later phase consumes.

### `Invocation` (dataclass, frozen)
Represents one spoke invocation line extracted from a runner prompt.
- `script_path: str` — the `.py` path as written in the prompt (e.g. `~/Research/four/examples/spokes/essay-pipeline.py`)
- `args: tuple[tuple[str, Optional[str]], ...]` — ordered `(flag, value)` pairs; flag includes leading dashes (`--goal`); value is `None` for a bare flag with no following value token.

### `ArgSpec` (dataclass, frozen)
Represents one argparse argument discovered in a spoke script (used by later phases).
- `name: str` — canonical option name without leading dashes (`goal`)
- `required: bool = False`
- `default: Optional[str] = None` — stringified default; `None` means "no explicit default"

## Why
Single source of truth for the extractor (Cycle 1) and the AST parser / diff engine (Cycles 3-7).

## Acceptance
- Both are importable from `spoke_lint.models`.
- `Invocation` is hashable/frozen; `.args` is a tuple (immutable, order-preserving).
- Helper `Invocation.flag_names() -> list[str]` returns the flags with dashes stripped.
