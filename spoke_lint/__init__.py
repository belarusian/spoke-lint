"""spoke-lint: static validator for pipeline runner prompts.

Diffs spoke invocations extracted from a runner prompt against the argparse
signatures of the referenced spoke scripts.
"""

from spoke_lint.extractor import extract_invocations
from spoke_lint.models import ArgSpec, Invocation

__all__ = ["Invocation", "ArgSpec", "extract_invocations"]
