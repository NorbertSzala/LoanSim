# Risk and optimization specification

Source: `source-requirements.md` §§12–15 and 33. Phase 4 is locked. This document names planned outputs and decision points, not an approved scoring model.

## Planned metrics and behavior

Cost rankings must identify the objective, units, included charges, comparison horizon, and assumed rate path. Safety views may include maximum mandatory payment, stressed income ratio, liquidity reserve, rate sensitivity, and budget breach. Show conflicting indicators as trade-offs. Stress paths and break-even scenarios are assumptions, not forecasts. Optimization must disclose variables, bounds, constraints, objective, infeasible results, ties, and Pareto dominance where applicable. Any chart must reconcile with validated engine results.

## Verification plan

Use hand-worked objective cases, non-comparable scenarios, infeasible constraints, multiple ties, Pareto dominated and non-dominated sets, stress boundary cases, and rate-path families with no or multiple break-even points. Verify that labels disclose assumptions and that results are reproducible from saved inputs.

## Owner decisions before implementation

Choose default cost and safety objectives, comparison rules, stress ranges, admissible forecast families, optimization bounds, treatment of missing data, and recommendation language. A weighted safety score versus a multi-criteria display has materially different interpretation; no default is approved.
