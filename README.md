# LoanSim

LoanSim is an offline desktop project for transparent mortgage simulations, comparisons, risk analysis, and exports. Phase 1 provides an I/O-free approximate monthly mortgage engine. Phase 2 adds a single-scenario PySide6 form, results, a balance chart, and local SQLite history.

## Current state

Phase 0 and Phase 1 met their local acceptance criteria and the hosted Ubuntu, macOS, and Windows CI gate for published commit `3642027` ([run `41320491886`](https://github.com/NorbertSzala/LoanSim/actions/runs/41320491886)). Phase 2 met its local GUI and SQLite criteria after independent audit repairs and its hosted three-system CI gate for published commit `07391f3` ([run `42482359059`](https://github.com/NorbertSzala/LoanSim/actions/runs/42482359059)). Phases 3–7 remain locked. The currently trusted SessionStart hook has a stale Phase 2 lock reminder; `AGENTS.md` and `harness/status.md` record current authorization. Native-window and Windows live-hook inspection remain unverified.

## Start here in a new checkout

1. Read `AGENTS.md`, `harness/status.md`, and `harness/decision-log.md` to identify the current authorization and unresolved decisions.
2. Read `docs/source-requirements.md` for the original requirements, then `PLANS.md` and the relevant `harness/build/phase-*.md` for the requested phase. Planned later phases grant no implementation permission.
3. Inspect `git status --short` before editing; the status document is a handoff, while Git shows the current local changes.
4. For verification, use the commands below and compare the results with the relevant notes in `harness/context/`. Report checks you actually ran and any platform limits.

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

The source specification also describes future analysis, reporting, and providers. These remain outside the Phase 2 single-scenario interface and the Phase 1 calculation core. Installation and verification evidence is recorded in the phase plans and `harness/build-log.md`.

## Install and verify

Use Python 3.11 or newer and [uv](https://docs.astral.sh/uv/). Install the locked package and development tools with `uv sync --locked --python 3.11`. Run `uv run --locked pytest -q`, `uv run --locked ruff check .codex/hooks src tests`, `uv run --locked ruff format --check .codex/hooks src tests`, and `uv run --locked mypy .codex/hooks src/loansim tests`. Launch the single-scenario window with `uv run --locked python -m loansim` (or `uv run --locked loansim`). Its SQLite history is stored under the platform application-data directory; set `LOANSIM_DATA_DIR` to use a chosen local directory. All Phase 2 interactions work offline.

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
