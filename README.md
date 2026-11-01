# LoanSim

LoanSim is an offline desktop project for transparent mortgage simulations, comparisons, risk analysis, and exports. The Phase 0 desktop shell remains minimal. Phase 1 is adding an I/O-free calculation core for approximate monthly mortgage scenarios.

## Current state

Phase 0 has a locally verified foundation. Phase 1 was explicitly authorized on 2026-10-25 and is complete against local criteria; Phases 2–7 remain locked. Hosted CI and the Windows hook path have not been verified in this session. Read `AGENTS.md` and `harness/status.md` before work.

## Start here in a new checkout

1. Read `AGENTS.md`, `harness/status.md`, and `harness/decision-log.md` to identify the current authorization and unresolved decisions.
2. Read `docs/source-requirements.md` for the original requirements, then `PLANS.md` and the relevant `harness/build/phase-*.md` for the requested phase. Planned later phases grant no implementation permission.
3. Inspect `git status --short` before editing; the status document is a handoff, while Git shows the current local changes.
4. For verification, use the commands below and compare the results with `harness/context/phase-00-foundation.md` and the Phase 1 context when available. Report checks you actually ran and any platform limits.

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

The source specification also describes future SQLite history, analysis, reporting, providers, and a product GUI. None is part of the Phase 1 calculation core. Installation and verification evidence is recorded in the phase plans and `harness/build-log.md`.

## Install and verify

Use Python 3.11 or newer and [uv](https://docs.astral.sh/uv/). Install the locked package and development tools with `uv sync --locked --python 3.11`. Run `uv run --locked pytest -q`, `uv run --locked ruff check .codex/hooks src tests`, `uv run --locked ruff format --check .codex/hooks src tests`, and `uv run --locked mypy .codex/hooks src/loansim tests`. Launch the minimal window with `uv run --locked python -m loansim` (or `uv run --locked loansim`); it contains no product loan-calculator workflow.

## Phase 1 calculation example

The engine accepts explicit `Decimal` inputs and returns an auditable schedule. This example is an estimate under twelve equal model periods per year, nominal annual interest divided by twelve, and cent settlement with `ROUND_HALF_UP`:

```python
from datetime import date
from decimal import Decimal

from loansim.core.amortization import simulate
from loansim.core.models import InstallmentType, LoanTerms
from loansim.core.rates import FixedRate

terms = LoanTerms(Decimal("1000.00"), 2, date(2026, 1, 1), InstallmentType.ANNUITY)
result = simulate(terms, FixedRate(Decimal("0.12")))
assert result.total_interest == Decimal("15.02")
assert result.rows[-1].closing_balance == Decimal("0.00")
```

The schedule exposes rate provenance, charges, mandatory and extra principal, actual monthly cash outflow including recurring own-funds charges, remaining balance, and an explicit estimate notice. Its simplified effective annual interest rate is a monthly-compounding conversion and is **not official RRSO**. See `docs/financial-assumptions.md` and `docs/mathematical-model.md` for formulas and exclusions. Phase 1 rejects recurring charges marked as financed.
