# Goals

## Product vision

Build an offline desktop application that helps users model and compare mortgage cash flows, costs, uncertainty, and risk. Results must be traceable to inputs, formulas, assumptions, and data sources. The initial interface may be Polish, with an architecture that allows later localization.

## Target users

People considering a mortgage and people reviewing an existing mortgage who need to explore repayment and cost scenarios offline. The tool supports their own decisions; it does not replace a lender's offer or professional advice.

## Intended outcomes

- Model individual loans with fixed, periodically fixed, and variable rates; annuity and declining schedules; fees; and overpayments.
- Compare named scenarios under explicit, comparable assumptions.
- Explain total costs, payment burden, sensitivity, stress scenarios, and optimization objectives without presenting uncertain outcomes as guarantees.
- Retain local simulation history and later export understandable PDF and XLSX reports.
- Permit future reference-rate data and historical analysis with visible provenance and offline operation.

## Success criteria for the eventual product

Calculations reconcile under documented conventions, financially material formulas have independent reference checks, the desktop workflow is usable offline, saved simulations remain reproducible, and exports match verified calculation results. Each criterion needs tests in its authorized implementation phase.

## Limits and non-goals

LoanSim is decision-support software, not a bank offer or a source of guaranteed future rates. Phase 0 provides a runnable startup shell and project foundation only. It does not deliver a financial calculation, product workflow, data integration, or report generator. Phases 1–7 require separate owner authorization.
