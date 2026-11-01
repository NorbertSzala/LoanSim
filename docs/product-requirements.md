# Product requirements

This is a navigable summary of owner-provided product scope in `source-requirements.md` sections 7–10, as narrowed for the approximate Phase 1 engine by the owner's 2026-10-25 decisions. It is not an implementation authorization. Requirement groups and status are tracked in `requirements-traceability.md`.

## Intended user workflow

The eventual standalone desktop application should let a user enter property, loan, interest, fee, and overpayment assumptions; derive missing values only when mathematically determined; simulate payment schedules; inspect auditable outputs; and later save, compare, and export scenarios. It must operate offline for core simulation work.

## Input families

- Property and financing: price, down payment amount and percentage, principal, LTV, currency, optional transaction costs, and financed costs.
- Loan terms: start, disbursement, and first-payment dates; term; initially monthly payments; annuity or declining installments; interest accrual, rounding, and charges. Phase 1 uses equal monthly model periods and one initial disbursement; displayed dates do not alter interest.
- Rates: fully fixed, periodically fixed, or index-plus-margin variable rates, with observation and reset dates, promotional changes, rate-path provenance, and missing-data policy. Phase 1 accepts a monthly path and explicitly labels a constant-future-rate continuation as a scenario.
- Overpayments: none, recurring, one-time, percentage, date-based, budget-limited, or custom schedules; reduce installment or shorten contractual term, while separately tracking actual total outflow. The owner-approved Phase 1 minimum is one-time or regular extra principal, fixed amount or combined-payment cap, with both repayment responses. The scope of other variants is still open.
- Charges: principal, interest, commissions, required and optional insurance, acquisition costs, taxes, early-repayment fees, and amendment fees must remain distinguishable.

Special-program support, including RKM, is optional and requires separately dated, verified program rules. Do not infer eligibility from a single down-payment percentage.

## Derivation and output rules

Entered and calculated values must remain distinguishable. Detect underdetermined, inconsistent, and overdetermined input sets; explain non-calculable values; retain provenance; and never silently overwrite conflicting input. Output should include payment-level principal, interest, overpayments, rate, dates, outstanding balance, cash outflows, cost totals, effective and contractual duration, and traceable assumptions. A carried-forward last rate is allowed only for future periods and must be labeled as a constant-rate scenario. Phase 1 uses a simplified effective annual rate with monthly compounding, never labeled as official RRSO; fuller dated-cash-flow RRSO is deferred.

## Open decisions

The owner approved the Phase 1 monthly period-interest model, rounding and allocation rules, installment recalculation, date labels, rate-path treatment, cost separation, supported input breadth, and simplified rate-metric scope on 2026-10-25, then explicitly authorized Phase 1. Treatment of a recurring charge marked as financed is still awaiting a separate answer; the engine rejects that combination until resolved. Program eligibility and fuller RRSO are deferred. See `financial-assumptions.md` and `mathematical-model.md`.
