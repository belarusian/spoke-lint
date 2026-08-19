"""Shared value objects for spoke-lint.

These frozen dataclasses are the single source of truth consumed by the
extractor (Cycle 1) and the later AST parser / diff engine (Cycles 3-7).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Invocation:
    """One spoke invocation line extracted from a runner prompt.

    Attributes:
        script_path: The ``.py`` path as written in the prompt, e.g.
            ``~/Research/four/examples/spokes/essay-pipeline.py``.
        args: Ordered ``(flag, value)`` pairs. The flag includes its leading
            dashes (e.g. ``--goal``); the value is ``None`` for a bare flag
            with no following value token.
    """

    script_path: str
    args: tuple[tuple[str, str | None], ...]

    def flag_names(self) -> list[str]:
        """Return the argument flags with leading dashes stripped.

        Order is preserved and matches the order of :attr:`args`.
        """
        return [flag.lstrip("-") for flag, _ in self.args]


@dataclass(frozen=True)
class ArgSpec:
    """One argparse argument discovered in a spoke script.

    Attributes:
        name: Canonical option name without leading dashes (e.g. ``goal``).
        required: Whether the argument is required by the spoke.
        default: Stringified default value; ``None`` means no explicit default.
    """

    name: str
    required: bool = False
    default: str | None = None
