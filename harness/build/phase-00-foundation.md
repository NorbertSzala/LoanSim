# Phase 0 — Repository foundation

## Status and boundary

The owner explicitly authorized the full Phase 0 foundation under `docs/source-requirements.md` §29 on 2026-10-24, superseding the earlier documentation-only boundary. The later 2026-10-24 message also authorized the third project skill, a small justified hook set, and exact-file Git staging after verification. On 2026-10-25 the owner requested staging of the remaining changes and GitHub push/merge, while keeping the local audit prompt ignored. An explicit commit order and a concrete merge path are still needed under `AGENTS.md`; the only observed remote branch is `master`. Phases 1–7 remain unauthorized. This file is the execution and acceptance plan for Phase 0, not authority for a later phase.

## Completed earlier documentation subset

Inventory the repository and `configure-cc/`; preserve owner files; establish root instructions, a roadmap, requirement links, domain summaries, a decision log, status, and a build log. Validate each coherent documentation change. Record unresolved choices and stop.

## Authorized foundation milestones

1. Update authorization records and requirement acceptance cases, then validate documentation and preservation.
2. Make the three owner-approved LoanSim skills Git-visible; audit imported skills and inspect their scripts without running them. Validate metadata and actual Codex discovery. Select only hooks with a documented purpose and verified contract; do not configure an agent merely to populate a directory.
3. Establish Python 3.11+ package metadata, a lockfile, a minimal entry point and PySide6 startup window, infrastructure smoke tests, and CI. Use a failing startup test before implementation and run targeted checks after each coherent change.
4. Verify lockfile installation in a clean environment, import, GUI startup, full tests, lint, type checks, CI configuration, instruction/skill structure, and final preservation and Git status.

Expected files are the `pyproject.toml` and `uv.lock` pair, `.github/workflows/ci.yml`, package entry and GUI shell under `src/loansim/`, tests under `tests/`, three project skill manifests, a bounded project hook, relevant nested instructions, and updated docs/harness files. The exact pre-change file list was presented to the owner in this task. The package exports no financial API.

Acceptance follows every criterion in source §29 plus the planning, handoff, skill, security, and independent-review duties in §§37–40 and the final appendix. A successful local CI syntax check does not prove a hosted Actions run. A configured hook is not operationally verified until Codex has trusted and executed its exact definition. Startup means the Qt event loop can create and show the minimal window; it does not imply a complete product workflow. The criterion-by-criterion evidence table belongs in `harness/context/phase-00-foundation.md`.

Risks: scope drift into product behavior, unsupported hook claims, accidental modification of the separate Claude checkout, and untracked or ignored work being missed in a handoff. Exclusions: financial calculations, application features, external integrations, export generators, and any Git history change without separate authorization.

Owner decisions recorded in `harness/decision-log.md`: Phase 0 authorization, Python 3.11+ minimum, three Git-visible LoanSim project skills, a small selected hook set, and exact-file staging after verification. No financial convention is approved. Open questions for later phases are listed in `docs/financial-assumptions.md` and the relevant phase plans.

## Dependencies, tests, and acceptance

Dependencies: the preserved source and clean `configure-cc/` checkout, an available Python 3.11 runtime, the locked `uv` project, and an offscreen-capable PySide6 environment. Local checks do not depend on GitHub Actions execution.

Test requirements: clean locked installation and package build, import, direct entry-point and offscreen window startup, all applicable pytest tests, Ruff lint and format, mypy, CI YAML and command parity, Markdown links and source hash, skill metadata and discovery, and controlled hook input/failure checks. Inspect fresh exit codes and output. Use temporary cache and build paths outside the checkout for final local verification.

Acceptance: every applicable §29 criterion has observed evidence; §§37–40 planning, context, log, and handoff records agree; all three skills are Git-visible and discoverable; imported skills remain untracked; and the selected hook's configuration, trust, and execution are reported separately. If any required item remains unverified, label the phase incomplete rather than silently deferring it.

Owner questions: future financial conventions, licensing and distribution choices, and any hook trust action that only the owner can grant. No pending question grants permission to begin a locked phase.
