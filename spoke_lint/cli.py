"""Command-line entry point for spoke-lint (Build Order phase 7).

This is the first user-facing surface of the tool. It is a **thin orchestration
layer**: all diffing semantics live in :mod:`spoke_lint.diff` and all rendering
semantics live in :mod:`spoke_lint.report`. This module only:

1. parses command-line arguments,
2. reads the runner prompt file,
3. runs the full lint pipeline (:func:`diff_prompt_full`),
4. renders the report (:func:`render_report`) and prints it to stdout,
5. returns a process exit code.

The exit-code contract is load-bearing for later automation:

- ``0`` — no findings (the rendered report is ``"OK"``).
- ``1`` — one or more findings were produced.
- ``2`` — usage / I/O error (e.g. the prompt file is missing or unreadable); an
  error message is written to stderr and no exception escapes :func:`run`.

Everything here is stdlib-only (``argparse``, ``sys``, ``pathlib``) and performs
no subprocesses, so it is fully testable in-process.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spoke_lint.diff import diff_prompt_full
from spoke_lint.report import render_report

#: Default directory searched for referenced spoke scripts.
DEFAULT_SPOKES_DIR: str = "./spokes"


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Pure function: no side effects, no I/O. The returned parser accepts:

    - ``prompt_file`` (positional): path to the runner prompt text file.
    - ``--spokes-dir``: directory containing the referenced spoke scripts
      (default :data:`DEFAULT_SPOKES_DIR`).
    - ``--path``: an optional **comma-separated** list of directories used to
      resolve gate-command executables. When omitted, the current process
      ``PATH`` is used downstream.

    Returns:
        A configured :class:`argparse.ArgumentParser`.
    """
    parser = argparse.ArgumentParser(
        prog="spoke-lint",
        description=(
            "Lint a runner prompt: diff spoke invocations against spoke argparse "
            "signatures and check gate-command tools, then print a deterministic "
            "report."
        ),
    )
    parser.add_argument(
        "prompt_file",
        help="Path to the runner prompt text file to lint.",
    )
    parser.add_argument(
        "--spokes-dir",
        default=DEFAULT_SPOKES_DIR,
        help=(
            "Directory containing the referenced spoke scripts "
            f"(default: {DEFAULT_SPOKES_DIR})."
        ),
    )
    parser.add_argument(
        "--path",
        default=None,
        metavar="DIRS",
        help=(
            "Comma-separated list of directories used to resolve gate-command "
            "executables. When omitted, the current process PATH is used."
        ),
    )
    return parser


def _split_path(raw: str | None) -> list[str] | None:
    """Split a comma-separated ``--path`` value into a list of directories.

    Returns ``None`` when ``raw`` is ``None`` (the option was not given), so the
    downstream pipeline falls back to the environment ``PATH``. Whitespace around
    each entry is stripped and empty entries are dropped.
    """
    if raw is None:
        return None
    parts = [part.strip() for part in raw.split(",")]
    return [part for part in parts if part]


def run(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code.

    Args:
        argv: Command-line arguments (without the program name). When ``None``,
            ``sys.argv[1:]`` is used.

    Returns:
        ``0`` when there are no findings, ``1`` when one or more findings exist,
        and ``2`` when the prompt file is missing or unreadable (an error message
        is written to stderr in that case; no exception escapes).
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    prompt_path = Path(args.prompt_file)
    try:
        text = prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"spoke-lint: error: cannot read prompt file {prompt_path}: {exc}", file=sys.stderr)
        return 2

    path = _split_path(args.path)
    findings = diff_prompt_full(text, Path(args.spokes_dir), path)
    report = render_report(findings)
    print(report)

    return 0 if not findings else 1


def main() -> None:
    """Console-script entry point.

    Thin wrapper around :func:`run` that exits the process with its return code.
    Only invoked under ``if __name__ == "__main__":`` (and via the installed
    ``spoke-lint`` console script).
    """
    sys.exit(run())


if __name__ == "__main__":
    main()
