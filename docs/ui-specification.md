# Desktop interface specification

Source: `source-requirements.md` §§8–11 and 31. Phase 2 was authorized on 2026-11-01 with the owner's `1A, 2A, 3A` choices in `harness/decision-log.md`. Phases 3–7 remain locked.

## Phase 2 workflow

The Polish form accepts one scenario at a time: property amounts and ratios, term, date, installment type, fixed/periodically fixed/variable rate paths, selected overpayments, and classified charges supported by the Phase 1 engine. Property and rate components show entered or derived origin, locks, and Polish formula explanations. A fixed annuity can derive a unique term from an entered payment. Invalid or conflicting input disables calculation and highlights the associated field or table where identifiable; stale derived values are cleared. Full schedule validation runs in a debounced worker before calculation becomes available. The engine retains formula ownership. Results show the payment schedule with mandatory principal and requested versus applied extra principal, named totals, the estimate notice, the rate-path context, a Qt balance chart, and the same balance series as a numeric table. Scenario names, colors, notes, save, reopen, copy, and confirmed deletion work offline. A pending save cannot be submitted twice or change the identity of a subsequently opened scenario. When open requests overlap, the most recent request wins. If saved form state cannot be restored, the current form remains intact and an error appears. Comparison, grouping, optimization, and exports remain later-phase scope.

## Interaction and accessibility tests

Use offscreen Qt interaction tests for entered/derived state, locks, conflicts, invalid metadata, rate-path gaps, financial-model inputs, a slow calculation, overlapping open requests, failed restoration, and the complete history flow. Saved input, derived provenance, and result snapshots are reopened without silent recalculation; saving an unchanged old result retains its engine version, while explicit recalculation uses the current engine. Editing starts a new validation cycle. Unsaved notes and inputs require explicit confirmation before replacement. The balance table provides periods, dates, and PLN units alongside the chart. Native-window and keyboard-assistive-technology inspection remain separate from offscreen automation.

Changing only the name, exact `#RRGGBB` color, or notes preserves the saved calculation, engine version, and derived provenance while updating the original form-state metadata. A failed open leaves existing field values, editability, and validation feedback intact. A late failure from an older open request does not mark a newer opened scenario invalid.

## Owner-approved choices

On 2026-11-01 the owner selected `1A` for the Polish form and input locks, `2A` for complete versioned snapshots and explicit deletion, and `3A` for a Qt-only balance chart, numeric table, and background calculation/storage. Presentation strings are centralized to permit a later English catalog. The hosted three-system CI gate passed for published commit `07391f3` ([run `42482359059`](https://github.com/NorbertSzala/LoanSim/actions/runs/42482359059)).
