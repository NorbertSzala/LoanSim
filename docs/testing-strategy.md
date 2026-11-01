# Verification strategy

This document describes Phase 0 checks and future product checks. Actual outcomes are recorded only in `harness/build-log.md`.

| Change type | Required evidence when implemented |
| --- | --- |
| Documentation and work rules | Markdown structure, local links, consistency of phase/status/decisions, preservation of source, read-only Git status, whitespace checks. |
| Financial engine | Independent reference formulas and schedules, golden cases, numerical invariants, property-based tests, edge cases, and regression tests for every material formula change. |
| GUI | Automated interactions, validation/error cases, offscreen startup smoke test, and visual inspection where available. |
| Persistence | Round-trip, versioned migration, integrity, deletion, and old-data preservation tests. |
| Providers | Mocked integration, offline behavior, missing data, source/date/unit provenance, and licensing review. |
| Analysis | Objective and constraint checks, infeasible and tied cases, sensitivity, Pareto correctness, and chart-to-engine reconciliation. |
| PDF/XLSX | Open/parse generated files, verify totals, units, sheets/pages, Unicode, assumptions, and source disclosure. |
| Configuration and hooks | Parse TOML/JSON, check supported schemas, run controlled valid and invalid inputs, verify actual hook registration and trust before calling a hook active. |

Use targeted checks after each coherent change, then a broader applicable suite before completion. Tests must be deterministic and run without a live external service. Do not disable a failing check or copy the implementation algorithm into the independent financial reference. Record exact commands and observed outcomes in `harness/build-log.md`.

Final phase closure requires an observed successful GitHub Actions run for the exact delivered commit. All three `ubuntu-latest`, `macos-latest`, and `windows-latest` jobs must complete successfully, including installation, import, tests, Ruff lint and format, mypy, and package build. A skipped downstream check or a green local run does not satisfy this gate. Record the run URL, commit SHA, and job conclusions in the phase handoff.

For Phase 0, verify a clean `uv sync` from the lockfile, package import, headless PySide6 window construction and startup, the complete pytest suite, Ruff, mypy, project skill metadata and discovery, CI syntax and command parity, and source/check-out preservation. A local CI parse cannot prove that GitHub Actions executed; report that limitation explicitly. The later owner-approved hosted CI gate applies before final Phase 0 closure.
