---
name: financial-model-review
description: Independently review LoanSim financial formulas, conventions, schedules, APR/RRSO assumptions, and numerical evidence in an explicitly authorized phase without modifying the work under review.
---

# Financial model review

Use this skill for an independent, read-only review of financially material LoanSim changes. Read `AGENTS.md`, `harness/status.md`, the applicable phase plan, owner-approved decisions, source requirements, and the calculation documentation. A review never authorizes a locked phase or settles an unapproved convention.

1. Identify the changed formula or model and its units, inputs, outputs, cash-flow dates, rate path, day-count, rounding, payment allocation, fee scope, and provenance. Separate documented decisions from assumptions and missing conventions.
2. Re-derive representative expected results without copying production code or its tests. Use a separate calculation, published reference with matching assumptions, or an independently prepared schedule; record the method and source.
3. Compare annuity and declining schedules where applicable, rate resets, overpayments, final partial payments, and APR/RRSO cash-flow timing and cost inclusion. Distinguish simplified metrics from contractual-style or lender-provided RRSO; refuse equivalence claims when required inputs are absent.
4. Check balance and allocation invariants, zero-rate and short-term cases, rounding boundaries, insufficient payments, conflicting inputs, and numerical regressions. Verify that tests would fail for a material error and investigate every discrepancy.
5. Report findings with file locations, severity, reproducible evidence, reference provenance, uncertainty, and decisions needed from the owner. Recheck a claimed fix independently and state what remains unverified.

Do not silently edit the implementation, tests, expected results, or decisions under review. Do not stage, commit, push, publish, approve a phase, or treat another agent's opinion as proof. Any Git action requires its own explicit owner authorization under `AGENTS.md`.
