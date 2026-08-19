"""Command-line entry point for spoke-lint (Build Order phase 7).

This is the first user-facing surface of the tool. It is a **thin orchestration
layer**: all diffing semantics live in :mod:`spoke_lint.diff` and all rendering
semantics live in :mod:`spoke_lint.report`. This module only:

1. parses command-line arguments (a ``check`` subcommand),
2. reads the runner prompt file,
3. runs the full lint pipeline (:func:`diff_prompt_full`),
4. renders the report (:func:`render_report`) and prints it to stdout,
5. returns a process exit code.

The CLI is a **subcommand** interface so the installed invocation documented in the
README — ``spoke-lint check <runner-prompt> --spokes-dir <dir>`` — works exactly as
written. There is currently one subcommand, ``check``, which carries all of the
linting behavior.

The exit-code contract is load-bearing for later automation:

- ``0`` — no findings (the rendered report is ``"OK"``).
- ``1`` — one or more findings were produced.
- ``2`` — usage / I/O error: the prompt file is missing or unreadable, **or** a
  subcommand is missing/unrecognized. An error message is written to stderr and no
  exception escapes :func:`run`.

Everything here is stdlib-only (``argparse``, ``sys``, ``pathlib``) and performs
no subprocesses, so it is fully testable in-process.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from spoke_lint.diff import diff_prompt_full
from spoke_lint.report import findings_to_json, render_report

#: Default directory searched for referenced spoke scripts.
DEFAULT_SPOKES_DIR: str = "./spokes"


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser.

    Pure function: no side effects, no I/O. The returned parser exposes a single
    **required** subcommand, ``check``, which carries the linting behavior:

    - ``prompt_file`` (positional): path to the runner prompt text file.
    - ``--spokes-dir``: directory containing the referenced spoke scripts
      (default :data:`DEFAULT_SPOKES_DIR`).
    - ``--path``: an optional **comma-separated** list of directories used to
      resolve gate-command executables. When omitted, the current process
      ``PATH`` is used downstream.

    A call with no subcommand (or an unrecognized one) is a usage error; argparse
    reports it and :func:`run` translates that into exit code ``2`` rather than
    letting the exception escape.

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
    subparsers = parser.add_subparsers(
        dest="command",
        metavar="{check}",
        required=True,
        title="subcommands",
    )

    check = subparsers.add_parser(
        "check",
        help=(
            "Lint a runner prompt file and print the deterministic report. Exit "
            "code 0 when clean, 1 when findings exist, 2 on usage/IO error."
        ),
        description=(
            "Read the runner prompt, diff spoke invocations against the referenced "
            "spoke scripts and check gate-command tools, then print a deterministic "
            "report to stdout."
        ),
    )
    check.add_argument(
        "prompt_file",
        help="Path to the runner prompt text file to lint.",
    )
    check.add_argument(
        "--spokes-dir",
        default=DEFAULT_SPOKES_DIR,
        help=(
            "Directory containing the referenced spoke scripts "
            f"(default: {DEFAULT_SPOKES_DIR})."
        ),
    )
    check.add_argument(
        "--path",
        default=None,
        metavar="DIRS",
        help=(
            "Comma-separated list of directories used to resolve gate-command "
            "executables. When omitted, the current process PATH is used."
        ),
    )
    check.add_argument(
        "--json",
        action="store_true",
        default=False,
        help=(
            "Emit findings as a machine-readable JSON array on stdout instead of "
            "the human report. The exit-code contract (0/1/2) is unchanged."
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


def _run_check(args: argparse.Namespace) -> int:
    """Execute the ``check`` subcommand and return its exit code.

    Reads the prompt file, runs the full lint pipeline, renders the report to
    stdout, and returns the contract exit code (``0`` clean / ``1`` findings /
    ``2`` I/O error). No exception escapes for a missing/unreadable prompt file.
    """
    prompt_path = Path(args.prompt_file)
    try:
        text = prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"spoke-lint: error: cannot read prompt file {prompt_path}: {exc}", file=sys.stderr)
        return 2

    path = _split_path(args.path)
    findings = diff_prompt_full(text, Path(args.spokes_dir), path)
    output = findings_to_json(findings) if args.json else render_report(findings)
    print(output)

    return 0 if not findings else 1


def run(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code.

    Args:
        argv: Command-line arguments (without the program name). When ``None``,
            ``sys.argv[1:]`` is used. The first token must be a subcommand
            (currently only ``check``).

    Returns:
        ``0`` when there are no findings, ``1`` when one or more findings exist,
        and ``2`` on a usage / I/O error — the prompt file is missing/unreadable,
        or a subcommand is missing/unrecognized. In the error cases an error message
        is written to stderr and no exception escapes :func:`run`.
    """
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse raises SystemExit(2) for a missing/unrecognized subcommand (or any
        # usage error). It has already printed its message to stderr; translate the
        # exit into a returned code so no exception escapes.
        code = exc.code
        if code is None:
            return 0
        return int(code)

    if args.command == "check":
        return _run_check(args)

    # Unreachable (the subcommand is required and only `check` exists), but keep a
    # defensive usage-error path so no exception escapes.
    print(f"spoke-lint: error: unknown subcommand {args.command!r}", file=sys.stderr)
    return 2


def main() -> None:
    """Console-script entry point.

    Thin wrapper around :func:`run` that exits the process with its return code.
    Only invoked under ``if __name__ == "__main__":`` (and via the installed
    ``spoke-lint`` console script).
    """
    sys.exit(run())


if __name__ == "__main__":
    main()
