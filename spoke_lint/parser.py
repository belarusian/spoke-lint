"""AST-based parser for spoke script argparse signatures.

Walks a spoke script's AST to find ``argparse.ArgumentParser`` bindings and
their ``.add_argument(...)`` calls, extracting one
:class:`~spoke_lint.models.ArgSpec` per argument in source order.
"""

from __future__ import annotations

import ast
from pathlib import Path

from spoke_lint.models import ArgSpec

_STORE_ACTIONS = frozenset({"store_true", "store_false", "count"})


def _find_parser_names(tree: ast.Module) -> set[str]:
    """Return the set of variable names bound to ``argparse.ArgumentParser(...)``."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        if (
            isinstance(func, ast.Attribute)
            and func.attr == "ArgumentParser"
            and isinstance(func.value, ast.Name)
            and func.value.id == "argparse"
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _extract_arg_spec(call: ast.Call) -> ArgSpec | None:
    """Extract an :class:`ArgSpec` from a single ``add_argument(...)`` call node.

    Returns ``None`` when the first positional argument is not a string literal.

    Rules (applied in order):
    1. **Positional argument**: if the first string literal has no leading dash,
       emit ``ArgSpec(name=<name>, required=True, default=None)`` regardless of
       any other keywords.
    2. **Store-type actions**: if an ``action=`` keyword is a string literal in
       ``{"store_true", "store_false", "count"}``, emit
       ``ArgSpec(name=<name>, required=False, default=None)`` and ignore any
       ``default=`` / ``type=`` keywords.
    3. **Default dashed-flag handling**: strip leading dashes, honour
       ``required=`` and ``default=`` keywords as before.
    """
    if not call.args:
        return None
    first = call.args[0]
    if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
        return None
    raw = first.value
    name = raw.lstrip("-")

    # Rule 1: positional argument (no leading dash)
    if not raw.startswith("-"):
        return ArgSpec(name=name, required=True, default=None)

    # Rule 2: store-type actions
    for kw in call.keywords:
        if kw.arg == "action":
            if (
                isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
                and kw.value.value in _STORE_ACTIONS
            ):
                return ArgSpec(name=name, required=False, default=None)
            break

    # Rule 3: default dashed-flag handling (existing behavior)
    required = False
    for kw in call.keywords:
        if kw.arg == "required":
            if isinstance(kw.value, ast.Constant) and kw.value.value is True:
                required = True
            break

    default: str | None = None
    for kw in call.keywords:
        if kw.arg == "default":
            try:
                val = ast.literal_eval(kw.value)
                default = None if val is None else str(val)
            except (ValueError, TypeError, SyntaxError):
                default = None
            break

    return ArgSpec(name=name, required=required, default=default)


def parse_spoke_args(path: str | Path) -> list[ArgSpec]:
    """Parse a spoke script and return its argparse argument specs in source order.

    Args:
        path: Path to the spoke script file.

    Returns:
        A list of :class:`~spoke_lint.models.ArgSpec` objects, one per
        ``add_argument`` call on a tracked ``ArgumentParser`` instance,
        in source order.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Spoke script not found: {p}")
    source = p.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(p))
    parser_names = _find_parser_names(tree)
    if not parser_names:
        return []

    candidates: list[tuple[int, ast.Call]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute):
            continue
        if func.attr != "add_argument":
            continue
        if not isinstance(func.value, ast.Name):
            continue
        if func.value.id not in parser_names:
            continue
        candidates.append((node.lineno, node))

    candidates.sort(key=lambda pair: pair[0])

    specs: list[ArgSpec] = []
    for _, call_node in candidates:
        spec = _extract_arg_spec(call_node)
        if spec is not None:
            specs.append(spec)
    return specs


def parse_spoke(path: str | Path) -> dict[str, ArgSpec]:
    """Parse a spoke script and return its arguments as a name-keyed dict.

    This is a convenience wrapper around :func:`parse_spoke_args` that returns
    ``{canonical_name: ArgSpec}`` for O(1) lookup by the diff engine.

    **Duplicate names: last one wins.** If the same canonical name appears in
    multiple ``add_argument`` calls, the later (last) spec overwrites the
    earlier one in the returned dict.

    Args:
        path: Path to the spoke script file.

    Returns:
        A dict mapping canonical argument names (dashes stripped) to their
        :class:`~spoke_lint.models.ArgSpec`.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
    """
    specs = parse_spoke_args(path)
    result: dict[str, ArgSpec] = {}
    for spec in specs:
        result[spec.name] = spec
    return result
