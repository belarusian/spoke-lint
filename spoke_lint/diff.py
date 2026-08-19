"""Diff engine: compare extracted invocations against spoke signatures.

This is the core of spoke-lint. It turns a runner prompt (or a single
invocation) into a deterministic list of :class:`~spoke_lint.models.Finding`
objects describing every mismatch between what the prompt passes and what the
referenced spoke scripts actually accept.
"""

from __future__ import annotations

from pathlib import Path

from spoke_lint.extractor import extract_invocations
from spoke_lint.gate import diff_gate_commands
from spoke_lint.models import ArgSpec, Finding, Invocation
from spoke_lint.parser import canonical_names, parse_spoke_args


def diff_invocation(invocation: Invocation, specs: list[ArgSpec]) -> list[Finding]:
    """Compare one invocation against a spoke's argument signature.

    Emits findings in a deterministic order:

    1. ``unknown_flag`` findings, one per passed flag whose canonical name is
       not in the accepted set, in **invocation order** (the order the flags
       appear in the prompt).
    2. ``missing_required`` findings, one per accepted spec with
       ``required=True`` whose name was not passed, in **signature order**
       (the order the specs appear in the spoke script).

    Args:
        invocation: The extracted invocation to check.
        specs: The spoke's argument specs (from :func:`parse_spoke_args`).

    Returns:
        A list of :class:`Finding`, empty when the invocation is fully valid.
    """
    accepted = canonical_names(specs)
    passed = invocation.flag_names()

    findings: list[Finding] = []

    # (a) unknown flags, in invocation order.
    for name in passed:
        if name not in accepted:
            findings.append(
                Finding(
                    kind="unknown_flag",
                    flag=name,
                    message=f"Unknown flag --{name} passed to {invocation.script_path}",
                )
            )

    # (b) missing required args, in signature order.
    for spec in specs:
        if spec.required and spec.name not in passed:
            findings.append(
                Finding(
                    kind="missing_required",
                    flag=spec.name,
                    message=f"Required flag --{spec.name} missing from {invocation.script_path}",
                )
            )

    return findings


def diff_prompt(text: str, spokes_dir: Path, path: list[str] | None = None) -> list[Finding]:
    """Diff every invocation in a prompt against the spokes under ``spokes_dir``.

    Top-level entry point. For each invocation (in document order):

    1. Resolve the script by taking the basename of ``invocation.script_path``
       and looking for it under ``spokes_dir``.
    2. If the resolved file does not exist, emit a single
       ``Finding("missing_script", <script_path>, ...)`` and continue — a bad
       reference never aborts the whole lint.
    3. Otherwise parse the script's signature and append the findings from
       :func:`diff_invocation`.

    Findings are aggregated in deterministic document order (invocation order;
    within an invocation, the ordering from :func:`diff_invocation`).

    Args:
        text: The runner prompt text.
        spokes_dir: Directory containing the referenced spoke scripts.
        path: An explicit list of directory paths used to resolve gate-command
            executables (see :func:`spoke_lint.gate.diff_gate_commands`). When
            ``None``, the current process ``PATH`` is used.

    Returns:
        A list of :class:`Finding`. Invocation findings come first (in document
        order), followed by gate-command findings (in document order). Empty
        when every invocation is fully valid and every gate tool is resolvable.
    """
    invocations = extract_invocations(text)
    findings: list[Finding] = []

    for invocation in invocations:
        basename = Path(invocation.script_path).name
        resolved = Path(spokes_dir) / basename

        if not resolved.exists():
            findings.append(
                Finding(
                    kind="missing_script",
                    flag=invocation.script_path,
                    message=f"Referenced script not found: {invocation.script_path}",
                )
            )
            continue

        specs = parse_spoke_args(resolved)
        findings.extend(diff_invocation(invocation, specs))

    # Gate-command findings come after all invocation findings, in document
    # order. This keeps the ordering deterministic and non-regressing for the
    # existing invocation behavior.
    findings.extend(diff_gate_commands(text, path))

    return findings
