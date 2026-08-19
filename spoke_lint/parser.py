"""AST-based parser for spoke script argparse signatures.

Walks a spoke script's AST to find ``argparse.ArgumentParser`` bindings and
their ``.add_argument(...)`` calls, extracting one
:class:`~spoke_lint.models.ArgSpec` per argument in source order.

Cycle 4 extends the parser with three real-world argparse shapes:
multiple option strings per argument (canonical long name), ``nargs=``
variants (required-ness), and sub-parser argument collection.
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


def _find_subparser_action_names(tree: ast.Module) -> set[str]:
    """Return variable names bound to the return value of ``add_subparsers(...)``.

    These names identify the subparser *action* object on which ``add_parser``
    is later called.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        if isinstance(func, ast.Attribute) and func.attr == "add_subparsers":
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


def _find_subparser_names(tree: ast.Module, action_names: set[str]) -> set[str]:
    """Return variable names bound to the return value of ``add_parser(...)``.

    Only ``add_parser`` calls made on a tracked subparser action object
    (see :func:`_find_subparser_action_names`) are considered.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Call):
            continue
        func = node.value.func
        if not (isinstance(func, ast.Attribute) and func.attr == "add_parser"):
            continue
        if not (isinstance(func.value, ast.Name) and func.value.id in action_names):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                names.add(target.id)
    return names


def _canonical_name(call: ast.Call) -> str | None:
    """Derive the canonical option name from an ``add_argument(...)`` call.

    Returns ``None`` when the first positional argument is not a string literal.

    Rules:
    - If any positional string literal is a long option (``--name``), the first
      such long option is the canonical name (dashes stripped).
    - Else, if short options (``-x``) are present, the first one wins (dashes
      stripped) — preserving the existing short-flag behavior.
    - Else (no dashed option strings) the argument is positional and the first
      string literal is its name.
    """
    if not call.args:
        return None
    first = call.args[0]
    if not isinstance(first, ast.Constant) or not isinstance(first.value, str):
        return None

    option_strings = [
        arg.value
        for arg in call.args
        if isinstance(arg, ast.Constant)
        and isinstance(arg.value, str)
        and arg.value.startswith("-")
    ]
    if option_strings:
        long_options = [opt for opt in option_strings if opt.startswith("--")]
        if long_options:
            return long_options[0].lstrip("-")
        return option_strings[0].lstrip("-")

    return first.value


def _nargs_value(call: ast.Call) -> str | int | None:
    """Return the ``nargs=`` keyword value if it is a string or int literal."""
    for kw in call.keywords:
        if kw.arg == "nargs":
            val = kw.value
            if isinstance(val, ast.Constant) and isinstance(val.value, (str, int)):
                return val.value
            return None
    return None


def _extract_arg_spec(call: ast.Call) -> ArgSpec | None:
    """Extract an :class:`ArgSpec` from a single ``add_argument(...)`` call node.

    Returns ``None`` when the first positional argument is not a string literal.

    Rules (applied in order):
    1. **Positional argument**: if the first string literal has no leading dash,
       the argument is required unless ``nargs=`` is ``"?"`` or ``"*"`` (in which
       case it is not required). ``default`` is always ``None`` for positionals.
    2. **Store-type actions**: if an ``action=`` keyword is a string literal in
       ``{"store_true", "store_false", "count"}``, emit
       ``ArgSpec(name=<name>, required=False, default=None)`` and ignore any
       ``default=`` / ``type=`` keywords.
    3. **Default dashed-flag handling**: strip leading dashes, honour
       ``required=`` and ``default=`` keywords. A ``nargs=`` of ``"?"`` or
       ``"*"`` keeps the flag not required (an explicit ``required=True`` still
       wins); ``"+"`` / integer keep the existing required/default handling.

    The canonical name is derived from the option-string rules in
    :func:`_canonical_name` (long option preferred over short).
    """
    name = _canonical_name(call)
    if name is None:
        return None

    # The first positional string literal is the argument's raw option/positional
    # string; a leading dash marks it as a dashed flag, otherwise it is positional.
    first = call.args[0]
    assert isinstance(first, ast.Constant) and isinstance(first.value, str)
    is_positional = not first.value.startswith("-")
    nargs_value = _nargs_value(call)

    # Rule 1: positional argument (no leading dash)
    if is_positional:
        if nargs_value in ("?", "*"):
            return ArgSpec(name=name, required=False, default=None)
        return ArgSpec(name=name, required=True, default=None)

    # Rule 2: store-type actions (dashed flags only)
    for kw in call.keywords:
        if kw.arg == "action":
            if (
                isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
                and kw.value.value in _STORE_ACTIONS
            ):
                return ArgSpec(name=name, required=False, default=None)
            break

    # Rule 3: default dashed-flag handling
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
        ``add_argument`` call on a tracked ``ArgumentParser`` instance or on a
        sub-parser created via ``add_subparsers()`` / ``add_parser(...)``,
        in source order (top-level and sub-parser args interleaved by line).

    Raises:
        FileNotFoundError: If ``path`` does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Spoke script not found: {p}")
    source = p.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(p))
    parser_names = _find_parser_names(tree)
    subparser_action_names = _find_subparser_action_names(tree)
    subparser_names = _find_subparser_names(tree, subparser_action_names)
    tracked = parser_names | subparser_names
    if not tracked:
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
        if func.value.id not in tracked:
            continue
        candidates.append((node.lineno, node))

    candidates.sort(key=lambda pair: pair[0])

    specs: list[ArgSpec] = []
    for _, call_node in candidates:
        spec = _extract_arg_spec(call_node)
        if spec is not None:
            specs.append(spec)
    return specs


def canonical_names(specs: list[ArgSpec]) -> set[str]:
    """Return the set of canonical accepted names from a list of :class:`ArgSpec`.

    Derived from the same extraction rules as :func:`parse_spoke_args`: each
    spec's ``name`` is already the canonical (prefix-free) name, so this is a
    cheap membership set for the diff engine.

    Args:
        specs: A list of :class:`~spoke_lint.models.ArgSpec`.

    Returns:
        The set of canonical names. An empty list yields an empty set.
    """
    return {spec.name for spec in specs}


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
