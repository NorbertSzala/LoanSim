# Test instructions

Keep tests deterministic, isolated, and offline. Phase 0 tests verify package import and GUI startup, including headless execution. Future financial tests must use independent references with documented fixture provenance, appropriate tolerances, edge cases, and regression cases for discovered defects; do not copy the implementation formula into the oracle. Never hide a failing check or report an unrun check as passed. The root `AGENTS.md` and current phase plan control scope.
