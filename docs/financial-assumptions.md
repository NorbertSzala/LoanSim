# Financial assumptions register

Source: `source-requirements.md` §§8–10 and 23. This is a list of decisions needed before Phase 1 calculations, not a set of defaults. The owner has approved no numerical convention.

| Decision | Viable alternatives | Consequence and evidence needed |
| --- | --- | --- |
| Interest accrual and day count | Calendar days with Actual/365, Actual/360, or product-specific basis; fixed period rate | Unequal months, partial periods, and shifted payment dates yield different interest. Obtain contract examples and independent reference schedules. |
| Precision and rounding | Round at each interest/payment event; retain extended precision until defined outputs | Balance, final payment, APR cash flows, and totals change. Specify currency precision, mode, points, and reconciliation tolerance. |
| Payment dates and partial periods | Calendar anniversary with business-day adjustment; fixed day; contractual dates | Payment timing and discounted cash-flow rates differ. Specify holiday and month-end handling. |
| Allocation and overpayment order | Fees → interest → scheduled principal → extra principal; another contract-specific order | Balance path and fee treatment change. Define insufficient and final-payment behavior. |
| Rate observation and reset | Observation on reset date, with lag, or product-specific fixing; missing observation rejects or uses a disclosed rule | Installments and historical reproducibility change. Define index tenor, publication date, effective date, and rounding. |
| Fixed-period expiry | Require explicit future path; use an owner-approved scenario family | No unknown future rate may be invented. Label scenario assumptions as forecasts, not observations. |
| APR/RRSO scope | Simplified informational metric; contractual-style calculation with complete mandatory cash flows | Legal meaning and comparability differ. Approve charges, dates, timing basis, algorithm, labels, and refusal conditions. |
| Early repayment | Shorten term; lower mandatory installment; explicit mixed strategy | Cash flows, savings, and contractual schedule differ. Define fees, minimum, locks, and final partial payment. |

Each selected convention needs an owner decision in `harness/decision-log.md`, formula documentation in `mathematical-model.md`, independent numerical references, and regression tests before implementation. FIN-007 and FIN-008 acceptance cases are in `requirements-traceability.md`.
