# Phase 1 — Financial calculation engine

Status: **LOCKED**. This plan grants no implementation authorization. Sources: `docs/source-requirements.md` §§8–10, 23, 30; `docs/requirements-traceability.md` FIN-001–009; `docs/financial-assumptions.md`.

## Objective, scope, and non-goals

Create typed inputs, validated derived values, annuity and declining schedules, fixed/periodically fixed/variable rate paths, margin, overpayments, fees, cost aggregation, and disclosed APR-related metrics. Keep calculation functions independent of GUI and I/O. Exclude product GUI, persistence, comparison, optimization, providers, and exports.

## Dependencies and milestones

Depends on a verified Phase 0 package and explicit owner approval of the relevant day-count, rounding, timing, reset, allocation, overpayment, and APR/RRSO conventions. Milestones: (1) approved convention and independent reference cases; (2) input/derived-value validation; (3) rate and schedule calculations; (4) overpayment, fees, totals, and APR-related metrics; (5) reconciliation and regression evidence.

## Expected files and tests

Expected future `src/loansim/core/` modules for models, interest, amortization, overpayments, costs, and APR, with `core/AGENTS.md`; targeted unit and independent numerical reference tests under `tests/`. Exact interfaces are to be decided in the authorized phase. Test FIN-007 and FIN-008 atomic cases, zero interest, partial periods, short terms, non-amortizing payments, rounding boundaries, rate resets, identical-cash-flow equivalence, final balance, and all monetary invariants.

## Acceptance, risks, and owner questions

Acceptance requires reproducible dated schedules, all Phase 1 FIN-007/008 outputs, auditable per-row records, independently checked numbers, and passing applicable quality checks. Main risks are plausible but incorrect amounts and mislabeled RRSO. Owner decisions: every convention in `docs/financial-assumptions.md`, permitted product variants, fee scope, and exact meaning of reported cost metrics. Do not fill gaps with silent defaults.
