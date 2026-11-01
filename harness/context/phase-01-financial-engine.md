# Phase 1 financial-engine context and local evidence

Updated: 2026-10-25. The owner explicitly authorized Phase 1 under the approximate monthly model and later selected own-funds-only recurring charges in `harness/decision-log.md`. This note records the implemented behavior and observed local checks. Phase 1 meets the locally verifiable §30 criteria. This does not authorize Phase 2, Git staging, a commit, or a push.

## Implemented boundary

- `src/loansim/core/` contains immutable validated inputs, bounded property and rate derivation, fixed/periodically fixed/variable rate schedules, a separate monthly interest-accrual function, annuity and declining schedules, overpayments, classified charge events, totals, and a simplified effective annual interest conversion. It imports no GUI or I/O service.
- Money is entered as exact PLN cents and settled with `Decimal` and `ROUND_HALF_UP`. Intermediate engine arithmetic uses a fixed 50-significant-digit context. A result carries the convention ID and an estimate notice. Period rows retain balances, mandatory and extra principal, cash outflow, displayed date, and rate provenance.
- Financed one-time charges at origination increase the initial debt once. Recurring charges are paid from own funds, appear as separate charge events and in each due month's actual cash outflow, and contribute to a separate incurred-recurring-charge total. A recurring charge marked as financed raises a clear validation error.
- `docs/financial-assumptions.md` and `docs/mathematical-model.md` state the approved conventions, formulas, timing, rounding points, and metric meanings. Full RRSO, Actual/365, GUI flows, providers, persistence, comparison, optimization, and exports remain outside this authorization.

## Observed verification

| Check | Result |
| --- | --- |
| Full offscreen `pytest -q` in the external Python 3.11.17 environment | Final run after the recurring-charge validation-order regression: 81 passed in 1.67 s, exit 0. Includes unit, boundary, regression, Hypothesis invariant, rate provenance, cost, and core-derivation cases. Earlier runs reported 75 and 80 passed before the additional cases. |
| Ruff lint and format on `.codex/hooks src tests` | All checks passed; 23 files already formatted; both exit 0. |
| Mypy on `.codex/hooks src/loansim tests` | No issues in 20 source files, exit 0 after a test-only optional-LTV narrowing fix. The preceding run found that one test typing error; it was not waived. |
| `uv lock --check --offline` with Python 3.11.17 | Resolved 17 packages, exit 0. It warned that the ignored repository `.venv` points to an expired temporary interpreter; the external verification environment worked. |
| `uv build --offline` | Source distribution and wheel built, exit 0. Latest archive inspection found the core modules in both artifact inventories and no ignored `VERIFY_PROGRESS_PROMPT.md` (`PHASE1_ARCHIVES_OK 18 69`). |
| Independent numerical checks | A `fractions.Fraction` annuity calculation, separate from production formulas, reproduced the published 32,000/36-month/0.5%-monthly case: payment 973.50, first interest 160.00, first closing balance 31,186.50 (`INDEPENDENT_FRACTION_REFERENCE_OK`, exit 0). An exact rational two-period mixed-charge reference reproduced interest/cash/closing balances `[(1100, 56826, 55274), (553, 56827, 0)]` in cents and total borrower cash 1,136.53 (`INDEPENDENT_MIXED_CHARGE_REFERENCE_OK`, exit 0). The published annuity reference is linked in `docs/mathematical-model.md`. |
| Core boundary and startup | AST scan found no GUI/network/database imports in seven `core` Python modules (`CORE_BOUNDARY_OK 7`, exit 0). The existing PySide6 entry point started and exited offscreen (`OFFSCREEN_STARTUP_OK`, exit 0; Qt emitted nonfatal font/size-hint messages). |
| Preservation and diff | `docs/source-requirements.md` SHA-256 remained `513377bf04f68e4447868944fe1a6b14856e677138c379511d9595340af9f89e`; `configure-cc/` status was empty; `git diff --check` exited 0. No Git staging, commit, or push was performed. |

Additional deterministic derivation probes covered 3,000 forward property cases, 3,000 cases with financed charges, and 5,000 inverse cases. Repeating-ratio and caller-context defects found in these checks have permanent regression tests.

## Local §30 acceptance and handoff

The owner selected variant A for recurring charges. Input, property, and rate derivation cases are in `test_core_models.py` and `test_core_derive.py`; fixed, periodically fixed, and variable rate paths in `test_core_rates.py`; annuity, declining, reset, overpayment, and rounding cases in `test_core_amortization.py`; fee timing, funding, budget burden, and cost reconciliation in `test_core_costs.py`; and broad numerical invariants in `test_core_properties.py`. The independent published and exact-rational references above cover financially material formulas. The final package and quality checks passed locally. Hosted CI, Windows hook execution, and native-window inspection were not observed here and are not claimed. The next phase remains locked pending a separate owner authorization; no Git staging, commit, or push was performed.
