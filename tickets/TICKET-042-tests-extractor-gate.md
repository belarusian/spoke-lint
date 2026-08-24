# TICKET-042 — fenced-code-block tests for extractor and gate

**Cycle:** 14
**Modules:** tests/test_extractor.py, tests/test_gate.py

## Capability
extractor: invocation inside a fence -> []; outside -> extracted (regression); fence with a non-spoke python snippet then a real spoke invocation outside -> only the real one; fence delimiter lines never treated as invocations; unclosed fence -> everything after ignored; language-tagged fence == bare fence. gate: gate tool inside a fence -> []; outside -> detected (regression); fence with pytest/ruff/mypy example lines + a real pytest outside -> only the real one; diff_gate_commands on a prompt whose only gate line is inside a code block yields NO missing_tool findings (hermetic PATH via monkeypatch.setenv). Hermetic; no host-PATH dependence.
