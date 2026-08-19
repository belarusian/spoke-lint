# TICKET-035 — report.findings_to_json: deterministic JSON serializer

**Cycle:** 10 (CLI phase, Build Order phase 7)
**Module:** `spoke_lint/report.py`

## Capability
Add a machine-readable serializer so downstream automation can consume findings as
structured JSON instead of parsing the human report.

### findings_to_json(findings: list[Finding]) -> str
- Serialize a list of :class:`~spoke_lint.models.Finding` to a deterministic JSON
  string.
- Top level is a JSON **array** in input order (no reordering — determinism comes
  from the caller passing already-ordered findings).
- Each finding becomes an object with exactly the keys ``kind``, ``flag``,
  ``message`` (matching the ``Finding`` dataclass fields), constructed explicitly in
  that fixed field order.
- Use ``json.dumps(..., ensure_ascii=False)``. No I/O.

## Rules
- stdlib-only (`json`). Pure function, no global state.
- Byte-deterministic: identical input yields byte-identical output across calls.
- Empty list serializes to the two-character string ``"[]"``.

## Acceptance
- `findings_to_json([]) == "[]"`.
- A single finding round-trips via `json.loads` to an object with the exact
  `kind`/`flag`/`message` values.
- Multiple findings preserve input order in the emitted array.
