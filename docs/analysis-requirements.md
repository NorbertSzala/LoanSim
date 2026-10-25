# Comparison, optimization, and risk requirements

Source: `source-requirements.md` sections 11–15. These are planned product requirements; Phases 3 and 4 remain locked.

## Comparison

Users should eventually create, duplicate, label, color, group, edit, save, and compare scenarios. Comparable views include principal balance, mandatory installments, actual payments, cumulative interest and charges, duration, rate paths, and overpayment impact. Any result involving unknown future rates must name its assumed path. Direct rankings require comparable principal, timing, fees, and other relevant conditions.

## Cost and safety criteria

Cheapest depends on an explicitly chosen objective: nominal interest, financing cost, present value, duration, initial cash, or required installment. Safety must use transparent indicators such as maximum mandatory payment, income ratio under stress, liquidity reserve, rate sensitivity, and budget breach. Conflicting safety criteria should be shown as trade-offs, not collapsed into an unexplained score.

## Optimization and analysis views

Use explicit variables, constraints, and objective functions. Start with an auditable search method when practical. Detect infeasibility, ties, dominated results, and sensitivity to assumptions. Multi-objective output should expose the Pareto frontier. Planned high-priority views are cost waterfall, fixed-versus-variable break-even analysis over specified rate-path families, stress tests, sensitivity heatmaps, and a synchronized scenario dashboard. Chart values must reconcile with the same calculation engine as numeric results.

## Unresolved before implementation

The owner must choose default ranking and safety criteria, permissible forecast families, treatment of incomparable scenarios, optimization search bounds, and whether any recommendation language is allowed. Stress examples in the source are scenarios, not forecasts. See `requirements-traceability.md` for phase and test mapping.
