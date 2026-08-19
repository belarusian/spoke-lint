# TICKET-024 — render_report + format_finding: deterministic human-readable report

**Cycle:** 7 (Reporting phase, Build Order phase 6)
**Module:** `spoke_lint/report.py` (new)

## Capability
Two pure functions that turn a list of :class:`Finding` into a stable,
human-readable multi-line string. No I/O.

### format_finding(finding: Finding) -> str
The single-line formatter. Deterministic and stable. Format:
`<kind>: <flag> — <message>` (em-dash separator). One line per finding, no trailing
newline. Exposed for reuse/testing.

### render_report(findings: list[Finding]) -> str
Group findings by `kind` in a **stable documented order**:
`missing_script`, `unknown_flag`, `missing_required`, `missing_tool`. Within each
group preserve the input (document) order. Emit one line per finding via
`format_finding`. Join lines with `\n`.

- Kinds not in the known set are appended after the known groups, sorted by kind
  name for determinism (forward-compat).
- Empty findings list → return a single `"OK"` line (no trailing newline).
- Pure function: same input always yields byte-identical output.

## Rules
- stdlib-only. No side effects, no I/O.
- The kind order is a module-level constant (`_KIND_ORDER`) so it is testable and
  stable across the CLI cycle.
- `render_report` must be expressible as: for each group in order, for each finding
  in that group (input order), append `format_finding(f)`.

## Acceptance
- `render_report([])` == `"OK"`.
- A single finding renders exactly one line equal to `format_finding(f)`.
- Mixed kinds render all groups in `_KIND_ORDER`; intra-group input order preserved.
- Output is deterministic (byte-stable across calls).
