"""Smoke test: the spoke_lint package must import cleanly."""


def test_import_spoke_lint():
    import spoke_lint

    assert spoke_lint is not None
