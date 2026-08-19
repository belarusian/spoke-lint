"""spoke-lint: static validator for pipeline runner prompts.

Diffs spoke invocations extracted from a runner prompt against the argparse
signatures of the referenced spoke scripts, and renders deterministic reports.
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
