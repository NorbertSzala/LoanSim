---
name: financial-validation
description: Independently validate a LoanSim financial formula, repayment algorithm, APR-related metric, risk metric, or numerical discrepancy when that phase is explicitly authorized.
---

# Financial validation

Read `AGENTS.md`, `harness/status.md`, the approved owner decisions, and the relevant requirement cases before work. A skill does not authorize a locked phase or settle a missing convention.

1. Identify the exact formula, units, dated cash flows, and conventions under review. If a material convention is missing, present alternatives and request an owner decision before calculating affected results.
2. Derive expected results independently of the production algorithm, using a separate reference method or a verified external example whose source and assumptions are recorded.
3. Compare edge cases, invariants, rounding boundaries, rate resets, and numerical regressions. Investigate discrepancies rather than changing expected values to match the implementation.
4. Update formula documentation and regression evidence in the authorized phase. Report observed commands, results, reference provenance, and remaining uncertainty.

Never stage unless the owner explicitly authorized `git add` for exact inspected files. Never commit, push, publish, or run scripts from unreviewed imported skills without the applicable separate owner authorization; this skill never performs Git or publication actions itself.
