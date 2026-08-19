"""Deterministic, human-readable rendering of diff findings.

This module is the **Reporting** layer (Build Order phase 6). It turns a list of
:class:`~spoke_lint.models.Finding` objects into a stable multi-line string that a
later CLI cycle can print verbatim. Everything here is a pure function: no I/O, no
global state, and byte-identical output for identical input so reports are
reproducible.

The grouping order is a documented contract (``_KIND_ORDER``). Findings of an
unknown kind — one not in that list — are appended after the known groups, sorted
by kind name, so forward-compat kinds still render deterministically.
"""

from __future__ import annotations

import json

from spoke_lint.models import Finding

#: Stable, documented order in which finding kinds are grouped in a report.
#: This is a contract: the CLI cycle relies on it to render a reproducible report.
_KIND_ORDER: tuple[str, ...] = (
    "missing_script",
    "unknown_flag",
    "missing_required",
    "missing_tool",
)

#: Separator between the ``kind: flag`` prefix and the human message.
_SEPARATOR: str = " — "


def format_finding(finding: Finding) -> str:
    """Render a single finding as one stable line.

    Format: ``<kind>: <flag> — <message>`` (em-dash separator). No trailing newline.

    Args:
        finding: The finding to render.

    Returns:
        A single-line string, deterministic for a given finding.
    """
    return f"{finding.kind}: {finding.flag}{_SEPARATOR}{finding.message}"


def _group_by_kind(findings: list[Finding]) -> list[tuple[str, list[Finding]]]:
    """Group findings by kind in the documented stable order.

    Known kinds (``_KIND_ORDER``) come first, in that order; any unknown kinds are
    appended after, sorted alphabetically by kind name for determinism. Within each
    group the original input (document) order is preserved. Empty groups are
    omitted.
    """
    buckets: dict[str, list[Finding]] = {}
    for finding in findings:
        buckets.setdefault(finding.kind, []).append(finding)

    ordered_kinds: list[str] = [k for k in _KIND_ORDER if k in buckets]
    ordered_kinds += sorted(k for k in buckets if k not in _KIND_ORDER)

    return [(kind, buckets[kind]) for kind in ordered_kinds]


def render_report(findings: list[Finding]) -> str:
    """Render a list of findings as a deterministic multi-line report.

    Findings are grouped by :attr:`Finding.kind` in the stable order
    ``missing_script``, ``unknown_flag``, ``missing_required``, ``missing_tool``
    (unknown kinds appended after, sorted by name). Within each group the input
    order is preserved. Each finding becomes one line via
    :func:`format_finding`; lines are joined with a single newline.

    Args:
        findings: The findings to render.

    Returns:
        A multi-line string (no trailing newline), or ``"OK"`` when there are no
        findings. Pure and deterministic: identical input yields byte-identical
        output.
    """
    if not findings:
        return "OK"

    lines: list[str] = []
    for _kind, group in _group_by_kind(findings):
        for finding in group:
            lines.append(format_finding(finding))

    return "\n".join(lines)


def findings_to_json(findings: list[Finding]) -> str:
    """Serialize a list of findings to a deterministic JSON string.

    The top level is a JSON **array** in input order (no reordering — determinism
    comes from the caller passing already-ordered findings). Each finding becomes an
    object with exactly the keys ``kind``, ``flag``, and ``message`` (matching the
    :class:`~spoke_lint.models.Finding` fields), constructed explicitly in that fixed
    field order.

    Args:
        findings: The findings to serialize, in the desired output order.

    Returns:
        A JSON array string (no trailing newline). An empty list serializes to the
        two-character string ``"[]"``. Pure and deterministic: identical input yields
        byte-identical output across calls.
    """
    objects = [
        {"kind": finding.kind, "flag": finding.flag, "message": finding.message}
        for finding in findings
    ]
    return json.dumps(objects, ensure_ascii=False)
