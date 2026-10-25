# Phase 3 — Comparison and visualization

Status: **LOCKED**. Source: `docs/source-requirements.md` §§11, 15.1, 15.4–15.5, 32; `docs/analysis-requirements.md`.

## Objective, scope, and non-goals

Compare named scenarios, payment and balance paths, interest, charges, duration, and assumptions. Add interactive comparison charts, cost waterfall, sensitivity views, grouping/filtering, and a synchronized dashboard. Exclude optimization ranking and forecast claims.

## Dependencies and milestones

Depends on reproducible Phase 1 results and Phase 2 scenario persistence. Milestones: (1) comparison data contract and comparability rules; (2) result tables and charts; (3) waterfall and sensitivity grids; (4) reconciliation and interaction verification.

## Expected files and tests

Expected future `src/loansim/analysis/` comparison/sensitivity modules and GUI views, with `analysis/AGENTS.md` and regression/GUI tests. Verify each plotted point and category against engine outputs, tie or mismatch disclosures, scenario edit refresh, missing or unknown rate paths, infeasible grid cells, and offline performance on representative inputs.

## Acceptance, risks, and owner questions

Acceptance requires synchronized, readable views whose values match validated engine results and disclose assumptions. Risks: false comparability and misleading scales. Owner decisions: comparability policy, default axes, color/accessibility rules, and treatment of unavailable data.
