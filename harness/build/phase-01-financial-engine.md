# Phase 1 — Financial calculation engine

Status: **COMPLETE AGAINST LOCALLY VERIFIABLE §30 CRITERIA** under the owner's explicit 2026-10-25 authorization and recurring-charge decision. Evidence: `harness/context/phase-01-financial-engine.md`. Sources: `docs/source-requirements.md` §§8–10, 23, 30; `harness/decision-log.md`; `docs/requirements-traceability.md` FIN-001–009; `docs/financial-assumptions.md`; `docs/mathematical-model.md`. Phases 2–7 remain locked.

## Objective, scope, and non-goals

Create typed inputs, validated derived values, annuity and declining schedules, fixed/periodically fixed/variable monthly rate paths, margin, selected overpayments, fees, cost aggregation, and a clearly labeled simplified effective annual interest rate. Use equal monthly periods and nominal annual interest divided by 12. Keep calculation functions independent of GUI and I/O. Exclude actual-day accrual, irregular periods, bank-specific settlement rules, full discounted-cash-flow RRSO, product GUI, persistence, comparison, optimization, providers, and exports. Retain an accrual boundary that can support a later Actual/365 convention.

## Dependencies and milestones

Depends on the locally verified Phase 0 package, the approved approximate-model conventions, and independent numerical references. The owner selected own-funds-only recurring charges; financed recurring inputs are invalid in Phase 1. Milestones: (1) record approved conventions and references; (2) input and derived-value validation; (3) rate and schedule calculations; (4) overpayment, fees, totals, and simplified rate metric; (5) reconciliation and regression evidence.

## Expected files and tests

Expected future `src/loansim/core/` modules for models, interest, amortization, overpayments, costs, and simplified rate metrics, with `core/AGENTS.md`; targeted unit and independent numerical reference tests under `tests/`. Exact interfaces are to be decided in the authorized phase. Test Phase 1 FIN-007 and FIN-008 atomic cases, zero interest, short terms, non-amortizing payments, rounding boundaries, rate resets, identical-cash-flow equivalence, final balance, and all monetary invariants. Actual-day and partial-period cases are deferred.

## Acceptance, risks, and owner questions

Acceptance requires reproducible model-period schedules with display dates, all assigned Phase 1 FIN-007/008 outputs, auditable per-row records, independently checked numbers, and passing applicable quality checks. The fuller RRSO and Phase 4 risk cases in the source are not Phase 1 completion criteria under the owner's newer scope decision. Main risks are plausible but incorrect amounts, misleading comparison labels, and mislabeling a rate conversion as RRSO. The owner approved the seven detailed choices and the own-funds-only recurring-charge rule recorded in `docs/financial-assumptions.md`.

## Test-first execution plan

Use the exact approved formulas and timing in `docs/mathematical-model.md`. Each task writes a focused failing test, runs it to confirm the intended failure, implements the minimum behavior, and reruns targeted tests. Follow with broader regression and quality checks; no task includes a Git action.

| Task | Production files | Tests and independent evidence |
| --- | --- | --- |
| 1. Public inputs and validation | `src/loansim/core/AGENTS.md`, `__init__.py`, `models.py` | `tests/test_core_models.py`: immutable typed inputs, PLN/cents, term/rate/date boundaries, unsupported combinations. |
| 2. Bidirectional derivation | `src/loansim/core/derive.py` | `tests/test_core_derive.py`: property/loan/LTV and rate-component equations, missing and conflicting input, provenance, locked entered values, repeat derivation. |
| 3. Rate paths and simplified metric | `src/loansim/core/rates.py`, `metrics.py`, `interest.py` | `tests/test_core_rates.py`, `test_core_amortization.py`: fixed, periodic, index plus margin, resets, missing historical observations, future continuation labels, publication timing, per-period effective rate, and date-independent monthly accrual. |
| 4. Schedules and charges | `src/loansim/core/amortization.py` | `tests/test_core_amortization.py`, `test_core_costs.py`: independent two-period and OpenStax references, both installment types, extra-payment strategies, budget limits, financed one-time costs, totals, final balance, and refusal cases. |
| 5. Invariants and handoff | No extra production module | `tests/test_core_properties.py`: seeded/property-based principal and cash-flow reconciliation, identical-cash-flow equivalence, monotonic interest under higher extra payments when assumptions permit it. Full pytest, Ruff, mypy, lock/install/build, documentation and source-preservation checks; record exact output in `harness/context/phase-01-financial-engine.md` and `harness/build-log.md`. |

The existing Phase 0 GUI startup remains unchanged. `core` must import no GUI, database, network, or reporting module. Financing a recurring charge when it becomes due is a possible later extension and is not implemented in Phase 1.
