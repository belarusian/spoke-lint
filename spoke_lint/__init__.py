"""spoke-lint: static validator for pipeline runner prompts.

Diffs spoke invocations extracted from a runner prompt against the argparse
signatures of the referenced spoke scripts.
"""

from spoke_lint.diff import diff_invocation, diff_prompt
from spoke_lint.extractor import extract_invocations
from spoke_lint.gate import diff_gate_commands, gate_commands
from spoke_lint.models import ArgSpec, Finding, Invocation
from spoke_lint.parser import canonical_names, parse_spoke, parse_spoke_args

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
    "gate_commands",
    "diff_gate_commands",
]
