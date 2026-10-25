# Mathematical model: constraints and open conventions

Source: `source-requirements.md` sections 8–10 and 23. This document records required behavior and unresolved conventions; it contains no implemented formula or owner-approved numerical assumption.

## Known requirements

- Use `Decimal` for monetary arithmetic, document precision and every rounding point, and preserve enough payment-level fields for an independent audit.
- Distinguish contractual installment obligations from voluntary overpayments and actual cash outflow. If two cases have identical dated cash flows, rates, and fees, they must yield identical balances and interest costs.
- Track interest model, reference-index definition, margin, observation dates, reset dates, rate-path source, and missing-data rule.
- Separate acquisition expenses from financing charges; do not infer that a 0% commission means no credit costs.
- Use discounted cash-flow timing for APR-related calculations, and label simplified RRSO separately from legally defined or lender-provided RRSO.
- Reconcile principal, interest, fees, and cash flows. Prevent negative final principal unless a documented handling rule permits it. Detect non-amortizing payments when no negative-amortization policy has been approved.

## Material questions requiring an owner decision

| Topic | Viable modeling alternatives and effect |
| --- | --- |
| Interest accrual | Calendar-day accrual with an explicit day-count basis versus period-rate accrual. Results differ for unequal months, partial periods, and payment-date shifts. |
| Day-count basis | Actual/365, Actual/360, or contract-specific basis. Each changes interest and must be tied to the modeled product or bank convention. |
| Rounding | Round interest and balances per event versus retain high precision and round displayed/payment values. This affects schedule totals and final payment. |
| Payment allocation | Specify the order of fees, accrued interest, scheduled principal, and overpayment. Different orders change balances and costs. |
| Rate resets | Specify observation lag, effective date, and behavior when a reference observation is missing. This changes each affected installment. |
| Periodically fixed expiry | Require a supplied follow-on rule or scenario; no default future rate is justified. |
| APR/RRSO scope | Decide which mandatory charges and dates belong in each disclosed metric, and whether a legally defined RRSO is in scope for a particular product. |
| Early repayment | Define fee timing, minimum payment, final partial payment, and whether contractual term or installment changes. |

Before implementation, present alternatives with worked consequences for the relevant product, seek explicit approval, and record the decision in `harness/decision-log.md`. Do not treat this table as approval of any option.

## Planned independent checks

Reference formula comparisons, independently derived schedules, golden examples, zero-rate and short-term cases, rounding boundaries, insufficient payments, rate resets, identical-cash-flow equivalence, and reconciliation invariants are required in the future authorized engine phase. Phase 0 startup tests exercise no financial formula; no financial test has run.
