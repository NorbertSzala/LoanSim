# Product requirements

This is a navigable summary of owner-provided product scope in `source-requirements.md` sections 7–10. It is not an implementation authorization. Requirement groups and status are tracked in `requirements-traceability.md`.

## Intended user workflow

The eventual standalone desktop application should let a user enter property, loan, interest, fee, and overpayment assumptions; derive missing values only when mathematically determined; simulate payment schedules; inspect auditable outputs; and later save, compare, and export scenarios. It must operate offline for core simulation work.

## Input families

- Property and financing: price, down payment amount and percentage, principal, LTV, currency, optional transaction costs, and financed costs.
- Loan terms: start, disbursement, and first-payment dates; term; initially monthly payments; annuity or declining installments; interest accrual, rounding, and charges.
- Rates: fully fixed, periodically fixed, or index-plus-margin variable rates, with observation and reset dates, promotional changes, rate-path provenance, and missing-data policy.
- Overpayments: none, recurring, one-time, percentage, date-based, budget-limited, or custom schedules; reduce installment or shorten contractual term, while separately tracking actual total outflow.
- Charges: principal, interest, commissions, required and optional insurance, acquisition costs, taxes, early-repayment fees, and amendment fees must remain distinguishable.

Special-program support, including RKM, is optional and requires separately dated, verified program rules. Do not infer eligibility from a single down-payment percentage.

## Derivation and output rules

Entered and calculated values must remain distinguishable. Detect underdetermined, inconsistent, and overdetermined input sets; explain non-calculable values; retain provenance; and never silently overwrite conflicting input or invent a future rate. Output should include payment-level principal, interest, overpayments, rate, dates, outstanding balance, cash outflows, cost totals, effective and contractual duration, and traceable assumptions. Keep simplified APR/RRSO distinct from any legally defined metric.

## Open decisions

Precise conventions for accrual, rounding, fees in APR/RRSO, payment allocation, partial periods, future rate paths, and program eligibility remain unresolved. See `mathematical-model.md`; implementation must stop on affected decisions and ask the owner with alternatives.
