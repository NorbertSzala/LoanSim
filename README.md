# LoanSim

LoanSim is a planned offline desktop tool for transparent mortgage simulations, comparisons, risk analysis, and exports. Phase 0 adds only a minimal startup shell; it does not calculate loans.

## Current state

Phase 0 has a locally verified foundation; hosted CI and the Windows hook path have not been observed. Phases 1–7 remain locked. Read `AGENTS.md` and `harness/status.md` before work.

## Start here in a new checkout

1. Read `AGENTS.md`, `harness/status.md`, and `harness/decision-log.md` to identify the current authorization and unresolved decisions.
2. Read `docs/source-requirements.md` for the original requirements, then `PLANS.md` and the relevant `harness/build/phase-*.md` for the requested phase. Planned later phases grant no implementation permission.
3. Inspect `git status --short` before editing; the status document is a handoff, while Git shows the current local changes.
4. For Phase 0 verification, use the commands below and compare the results with `harness/context/phase-00-foundation.md`. Report checks you actually ran and any platform limits.

Repository instructions, plans, decisions, reviewed project skills, and the shared hook belong in Git. `VERIFY_PROGRESS_PROMPT.md`, imported third-party skills, environments, caches, and secrets remain local or ignored. A fresh checkout may not contain the optional audit prompt.

## Document map

- `docs/source-requirements.md`: original owner-provided product and workflow source; preserve unchanged.
- `VERIFY_PROGRESS_PROMPT.md`: optional owner-provided local checklist for independent, read-only audits; Git ignores it, so fresh checkouts may not contain it.
- `GOALS.md`: product intent and limitations.
- `PLANS.md`: phase roadmap and authorization state.
- `PROMPTS.md`: reusable prompts that retain owner control.
- `docs/requirements-traceability.md`: grouped source-to-phase register; unresolved details remain visible.
- `docs/repository-audit.md` and `docs/codex-migration.md`: baseline inventory and Claude-to-Codex assessment.
- `harness/status.md`, `harness/decision-log.md`, and `harness/build-log.md`: current permission, owner decisions, and observed work.

The source specification describes future financial calculations, SQLite history, analysis, and reporting. A startup shell is only a foundation smoke target. Installation and verification commands are recorded in `harness/build/phase-00-foundation.md` and `harness/build-log.md` once executed.

## Phase 0 startup

Use Python 3.11 or newer and [uv](https://docs.astral.sh/uv/). Install the locked package and development tools with `uv sync --locked --python 3.11`. Launch the minimal window with `uv run --locked python -m loansim` (or `uv run --locked loansim`). The window contains no loan calculator. Run the foundation checks with `uv run --locked pytest -q`, `uv run --locked ruff check src tests`, and `uv run --locked mypy src/loansim tests`.
