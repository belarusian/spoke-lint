"""Public API surface test: assert the documented public surface of spoke_lint.

This is a small, deterministic, dependency-free guard that the stable public
surface (``spoke_lint.__all__``) is coherent and that the module docstring
documents the exit-code contract and the layering. It complements
``tests/test_package.py`` (which pins the exact ``__all__`` list and object
identity) by asserting *kinds* of names and the documented prose.
"""

from __future__ import annotations

import spoke_lint

# The three value-object dataclasses are classes; every other public name is a
# callable entry point. This split is the documented shape of the API.
_DATACLASSES = {"Invocation", "ArgSpec", "Finding"}


def test_all_names_are_importable():
    """Every name in ``__all__`` resolves to an attribute on the package."""
    for name in spoke_lint.__all__:
        assert hasattr(spoke_lint, name), f"{name} is in __all__ but not importable"


def test_dataclasses_are_classes_and_rest_callable():
    """Dataclasses are classes; every other public name is callable."""
    for name in spoke_lint.__all__:
        obj = getattr(spoke_lint, name)
        if name in _DATACLASSES:
            assert isinstance(obj, type), f"{name} should be a class"
        else:
            assert callable(obj), f"{name} should be callable"


def test_no_public_name_is_missing():
    """``__all__`` is non-empty and has no duplicates."""
    assert spoke_lint.__all__, "__all__ must not be empty"
    assert len(spoke_lint.__all__) == len(set(spoke_lint.__all__)), "no duplicate names in __all__"


def test_module_docstring_documents_exit_code_contract():
    """The module docstring mentions the exit-code contract (0, 1, 2)."""
    doc = spoke_lint.__doc__ or ""
    for code in ("0", "1", "2"):
        assert code in doc, f"module docstring should mention exit code {code}"


def test_module_docstring_documents_layering():
    """The module docstring names the pipeline layers."""
    doc = spoke_lint.__doc__ or ""
    for layer in ("extractor", "parser", "diff", "report", "cli"):
        assert layer in doc, f"module docstring should mention the {layer} layer"


def test_module_docstring_mentions_purpose():
    """The module docstring states the package's purpose."""
    doc = (spoke_lint.__doc__ or "").lower()
    assert "runner prompt" in doc or "spoke" in doc, "module docstring should state its purpose"
