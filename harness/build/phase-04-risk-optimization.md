# Phase 4 — Risk and optimization

Status: **LOCKED**. Source: `docs/source-requirements.md` §§12–15, 33; `docs/risk-model.md`.

## Objective, scope, and non-goals

Provide transparent cheapest and safest criteria, stress tests, fixed/variable break-even, constrained optimization, sensitivity, and Pareto results. No guaranteed prediction, hidden score, or objective-free recommendation.

## Dependencies and milestones

Depends on validated scenarios and approved metric/forecast choices. Milestones: (1) objective and risk definitions with reference cases; (2) stress and break-even analysis; (3) constrained search and Pareto; (4) disclosure and regression review.

## Expected files and tests

Expected future `src/loansim/analysis/` risk, optimization, break-even modules and GUI views with independent metric tests. Cover incomparable cases, infeasibility, ties, dominated results, multiple or absent break-even roots, constraint boundaries, rate shock paths, and reproducible outputs.

## Acceptance, risks, and owner questions

Acceptance requires named objectives and constraints, correct rankings and Pareto sets, explicit uncertainty, and passing independent cases. Risks: seemingly objective advice from arbitrary assumptions. Owner decisions: defaults, constraints, rates/path families, search bounds, and wording of advice.
