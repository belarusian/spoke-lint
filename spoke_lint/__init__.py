"""spoke-lint: static validator for four pipeline runner prompts.

Purpose
-------
Given a runner prompt (free-form text that interleaves *spoke invocation* lines,
*gate* commands, and prose) and a directory of spoke scripts, ``spoke-lint``
diffs what the prompt passes against what each referenced spoke actually accepts,
and renders a deterministic report (human-readable or JSON).

Layering
--------
The package is layered so each stage is independently testable:

1. **extractor** (:mod:`spoke_lint.extractor`) — turn prompt text into structured
   :class:`~spoke_lint.models.Invocation` objects, in document order.
2. **parser** (:mod:`spoke_lint.parser`) — walk a spoke script's AST to discover its
   ``argparse`` argument signatures as :class:`~spoke_lint.models.ArgSpec`.
3. **diff** (:mod:`spoke_lint.diff`) — compare invocations against signatures and
   emit :class:`~spoke_lint.models.Finding` objects; also checks gate commands
   (:mod:`spoke_lint.gate`).
4. **report** (:mod:`spoke_lint.report`) — render findings deterministically as a
   human report or a JSON array.
5. **cli** (:mod:`spoke_lint.cli`) — the thin orchestration layer that wires the
   stages together behind the ``check`` subcommand.

Exit-code contract
------------------
The CLI (and :func:`run`) return a process exit code that downstream automation
relies on:

- ``0`` — no findings (the rendered report is ``"OK"`` / JSON ``[]``).
- ``1`` — one or more findings were produced.
- ``2`` — usage / I/O error (missing/unreadable prompt file, or a missing or
  unrecognized subcommand). An error message goes to stderr and no exception
  escapes :func:`run`.

Public API
----------
The names in :data:`__all__` below are the stable public surface. The three
dataclasses (:class:`~spoke_lint.models.Invocation`,
:class:`~spoke_lint.models.ArgSpec`, :class:`~spoke_lint.models.Finding`) are the
value objects shared across layers; the remaining names are the per-stage entry
points, re-exported here so callers can ``from spoke_lint import ...``.
"""

from spoke_lint.cli import build_parser, run
from spoke_lint.diff import diff_invocation, diff_prompt, diff_prompt_full
from spoke_lint.extractor import extract_invocations
from spoke_lint.gate import diff_gate_commands, gate_commands
from spoke_lint.models import ArgSpec, Finding, Invocation
from spoke_lint.parser import canonical_names, parse_spoke, parse_spoke_args
from spoke_lint.report import findings_to_json, format_finding, render_report

__all__ = [
    "Invocation",
    "ArgSpec",
    "Finding",
    "extract_invocations",
    "parse_spoke_args",
    "parse_spoke",
    "canonical_names",
    "diff_invocation",
    "diff_prompt",
    "diff_prompt_full",
    "gate_commands",
    "diff_gate_commands",
    "findings_to_json",
    "format_finding",
    "render_report",
    "build_parser",
    "run",
]
