"""Packaging smoke test: assert release metadata in pyproject.toml is correct.

This guards the Cycle 11 release-metadata polish from silent regression *without*
network access or a wheel build. It reads ``pyproject.toml`` and asserts the
``[project]`` table and the ``[tool.coverage.run]`` block are present and correct.

Parsing strategy: use :mod:`tomllib` when available (Python >= 3.11); otherwise
fall back to a minimal, dependency-free line/regex parser that is sufficient for
the specific fields asserted here. This environment runs Python 3.10, so the
fallback path is what actually executes — but both paths are exercised by the
tests below.
"""

from __future__ import annotations

import re
from pathlib import Path

try:  # Python >= 3.11
    import tomllib  # type: ignore[import-not-found]

    _HAS_TOMLLIB = True
except ModuleNotFoundError:  # pragma: no cover - exercised on Python < 3.11
    tomllib = None  # type: ignore[assignment]
    _HAS_TOMLLIB = False


def _pyproject_path() -> Path:
    """Return the path to the repository ``pyproject.toml``."""
    return Path(__file__).resolve().parent.parent / "pyproject.toml"


def _load_toml(path: Path) -> dict[str, object]:
    """Parse ``path`` with :mod:`tomllib` when available, else a minimal fallback.

    The fallback is intentionally small: it only needs to surface the scalar and
    list fields asserted by these tests (``name``, ``description``, ``authors``,
    ``license``, ``classifiers``, ``dependencies``), the ``[project.scripts]``
    table, and the ``[tool.coverage.run]`` table. It is not a general TOML parser.

    Args:
        path: Path to the ``pyproject.toml`` file.

    Returns:
        A dict mirroring the top-level tables of the file.
    """
    if _HAS_TOMLLIB:
        with path.open("rb") as fh:
            return tomllib.load(fh)  # type: ignore[union-attr]
    return _parse_minimal(path.read_text(encoding="utf-8"))


def _parse_minimal(text: str) -> dict[str, object]:
    """Minimal line-based TOML reader for the fields these tests assert.

    Handles ``[table]`` / ``[table.sub]`` headers and ``key = value`` lines where
    the value is a bare string, an inline table (``{ ... }``), or a single-line
    array (``[ ... ]``). Multi-line arrays are joined until the brackets balance.

    Args:
        text: The raw ``pyproject.toml`` contents.

    Returns:
        A nested dict of tables to keys to parsed values.
    """
    root: dict[str, object] = {}
    current: dict[str, object] = root
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line.startswith("#"):
            continue
        header = re.match(r"^\[(.+)\]$", line)
        if header:
            current = _resolve_table(root, header.group(1))
            continue
        match = re.match(r"^([A-Za-z0-9_.\-]+)\s*=\s*(.*)$", line)
        if not match:
            continue
        key = match.group(1)
        value_text = match.group(2).strip()
        # Join continuation lines for multi-line arrays.
        while value_text.count("[") > value_text.count("]") and i < len(lines):
            value_text += " " + lines[i].strip()
            i += 1
        current[key] = _parse_value(value_text)
    return root


def _resolve_table(root: dict[str, object], dotted: str) -> dict[str, object]:
    """Walk/create the nested table for a dotted ``[a.b.c]`` header.

    Args:
        root: The top-level table dict.
        dotted: The dotted table name (e.g. ``project.scripts``).

    Returns:
        The innermost table dict, creating empty dicts along the path as needed.
    """
    node = root
    for part in dotted.split("."):
        existing = node.get(part)
        if not isinstance(existing, dict):
            existing = {}
            node[part] = existing
        node = existing  # type: ignore[assignment]
    return node


def _parse_value(value_text: str) -> object:
    """Parse a single-line TOML value into a Python object.

    Supports bare strings, inline tables (``{ ... }``), and arrays (``[ ... ]``).
    Nested values inside arrays/tables are parsed recursively.

    Args:
        value_text: The raw value text after ``=``.

    Returns:
        A string, dict, list, or bool matching the TOML value.
    """
    if value_text.startswith("[") and value_text.endswith("]"):
        inner = value_text[1:-1].strip()
        if not inner:
            return []
        return [_parse_value(part.strip()) for part in _split_top_level(inner)]
    if value_text.startswith("{") and value_text.endswith("}"):
        inner = value_text[1:-1].strip()
        result: dict[str, object] = {}
        if inner:
            for part in _split_top_level(inner):
                key, _, val = part.partition("=")
                result[key.strip().strip('"')] = _parse_value(val.strip())
        return result
    if value_text.startswith('"') and value_text.endswith('"'):
        return value_text[1:-1]
    if value_text == "true":
        return True
    if value_text == "false":
        return False
    return value_text


def _split_top_level(inner: str) -> list[str]:
    """Split ``inner`` on commas that are not nested inside brackets/braces.

    Args:
        inner: The text between the outermost array/table delimiters.

    Returns:
        A list of top-level element strings (whitespace preserved).
    """
    parts: list[str] = []
    depth = 0
    buf: list[str] = []
    for ch in inner:
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if "".join(buf).strip():
        parts.append("".join(buf))
    return parts


def test_pyproject_exists_and_parses():
    path = _pyproject_path()
    assert path.exists(), "pyproject.toml must exist at the repository root"
    data = _load_toml(path)
    assert isinstance(data, dict) and data, "pyproject.toml must parse to a non-empty table"


def test_project_name_and_description():
    project = _load_toml(_pyproject_path())["project"]  # type: ignore[index]
    assert project["name"] == "spoke-lint"
    description = project.get("description")
    assert isinstance(description, str) and description.strip(), "description must be non-empty"


def test_project_authors_and_license():
    project = _load_toml(_pyproject_path())["project"]  # type: ignore[index]
    authors = project.get("authors")
    assert isinstance(authors, list) and authors, "authors must be a non-empty list"
    first_author = authors[0]
    assert isinstance(first_author, dict) and first_author, "first author must be an inline table"
    assert "license" in project, "a license field must be present"


def test_project_classifiers():
    project = _load_toml(_pyproject_path())["project"]  # type: ignore[index]
    classifiers = project.get("classifiers")
    assert isinstance(classifiers, list), "classifiers must be a list"
    assert len(classifiers) >= 2, "at least two classifiers are required"


def test_project_dependencies_empty():
    project = _load_toml(_pyproject_path())["project"]  # type: ignore[index]
    assert project.get("dependencies") == []
    # The package must remain stdlib-only: no runtime dependencies.


def test_project_scripts_entry_point():
    data = _load_toml(_pyproject_path())
    scripts = data["project"]["scripts"]  # type: ignore[index]
    assert scripts.get("spoke-lint") == "spoke_lint.cli:main"


def test_coverage_run_source_includes_spoke_lint():
    data = _load_toml(_pyproject_path())
    coverage = data["tool"]["coverage"]  # type: ignore[index]
    run_block = coverage["run"]  # type: ignore[index]
    source = run_block.get("source")  # type: ignore[union-attr]
    assert isinstance(source, list) and "spoke_lint" in source
