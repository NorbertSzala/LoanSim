# Requirements traceability register

This register classifies the **numbered source sections and major subsections**, rather than each individual bullet, in `source-requirements.md`. The source remains unchanged. `SOURCE` means owner-provided product or process scope, **not** approval to implement a locked phase or a missing convention. `OPEN` means an owner decision is needed. `APPROVED` refers only to explicit decisions recorded in `harness/decision-log.md`. Acceptance and test columns describe future evidence, not tests already run.

| ID | Original source | Target area | Phase | Acceptance criterion | Planned verification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| GOV-001 | §§0–6: role, decisions, phases, Git, testing, communication | Repository policy | All | Phase boundaries and human gates are explicit. | Instruction/status consistency review. | APPROVED current rule |
| PRD-001 | §7: offline desktop vision and result provenance | Product | 2–7 | Core use works offline; results disclose inputs and assumptions. | Offline smoke and result audit. | SOURCE / LOCKED |
| FIN-001 | §8 property information | `core` inputs | 1 | Property, down payment, principal, LTV, currency, and costs are represented. | Model validation and equation tests. | SOURCE / LOCKED |
| FIN-002 | §8 loan parameters | `core` inputs | 1 | Dates, term, frequency, schedule type, and charges are explicit. | Boundary and date tests. | SOURCE / LOCKED |
| FIN-003 | §8 rate configuration | `core`, `providers` | 1, 6 | Fixed, periodically fixed, and variable paths retain index and dates. | Reset and provenance tests. | SOURCE / LOCKED |
| FIN-004 | §8 early repayment | `core` | 1 | Supported schedules and responses distinguish obligation from actual outflow. | Cash-flow equivalence and fee tests. | SOURCE / LOCKED |
| FIN-005 | §8 fees and expenses | `core` | 1 | Financing charges and acquisition expenses stay separate. | Cost reconciliation tests. | SOURCE / LOCKED |
| FIN-006 | §8 RKM and special programs | `core` extension | 7 | Rules are dated and verified before any eligibility result. | Program-rule cases against approved source. | OPEN detail / LOCKED |
| FIN-007 | §9 missing-value calculation | `core`, `gui` | 1, 2 | All §9 candidate values and eleven behavior rules are mapped below. | FIN-007 case matrix below. | SOURCE / LOCKED |
| FIN-008 | §10 simulation outputs | `core`, `analysis`, `gui` | 1–4 | Every §10 output and APR/RRSO disclosure rule is mapped below. | FIN-008 case matrix below. | SOURCE / LOCKED |
| ANA-001 | §11 multiple scenarios | `analysis`, `gui`, `data` | 2, 3 | Named scenarios and comparable time-series views work. | Scenario round-trip and chart tests. | SOURCE / LOCKED |
| ANA-002 | §12 cheapest criteria | `analysis` | 4 | Ranking names its objective and applicable rate path. | Objective and comparability cases. | SOURCE / LOCKED |
| ANA-003 | §13 safest criteria | `analysis` | 4 | Transparent indicators and conflicting trade-offs are shown. | Metric and stress cases. | OPEN defaults / LOCKED |
| ANA-004 | §14 optimization and Pareto | `analysis` | 4 | Explicit constraints; infeasibility, ties, and dominance handled. | Search and Pareto reference cases. | SOURCE / LOCKED |
| ANA-005 | §15.1 cost waterfall | `analysis`, `gui` | 3 | Chart categories reconcile with financial totals. | Chart-to-engine totals. | SOURCE / LOCKED |
| ANA-006 | §15.2 fixed/variable break-even | `analysis` | 4 | Rate-path family is disclosed; no false unique solution. | Analytical and multiple-root cases. | OPEN path family / LOCKED |
| ANA-007 | §15.3 stress testing | `analysis` | 4 | Shocks are labeled as assumptions, not forecasts. | Stress scenario regression. | SOURCE / LOCKED |
| ANA-008 | §15.4 sensitivity heatmaps | `analysis`, `gui` | 3, 4 | Values and infeasible combinations are identified. | Grid and visualization tests. | SOURCE / LOCKED |
| ANA-009 | §15.5 comparison dashboard | `analysis`, `gui` | 3 | Synchronized results and ranking disclosures. | GUI and data reconciliation. | SOURCE / LOCKED |
| DATA-001 | §16 persistent history | `data` | 2 | Inputs, conventions, timestamps, versions, and provenance survive reopen. | Round-trip and migration tests. | SOURCE / LOCKED |
| EXP-001 | §17 XLSX | `reporting` | 5 | Workbook is readable with verified values and source notes. | Open workbook, inspect structure and totals. | SOURCE / LOCKED |
| EXP-002 | §18 PDF | `reporting` | 5 | Readable Unicode report discloses assumptions and totals. | Parse and visually inspect representative PDF. | SOURCE / LOCKED |
| PROV-001 | §19 reference-rate data | `providers` | 6 | Verified sources, definitions, dates, licensing, and offline fallback. | Mocked, missing-data, and provenance tests. | OPEN providers / LOCKED |
| PROV-002 | §20 historical backtesting | `providers`, `analysis` | 6 | Actual, reconstructed, proxy, and synthetic paths are distinguished. | Historical-source and reproducibility tests. | OPEN proxies / LOCKED |
| ARCH-001 | §21 preferred stack | Project configuration | 0–7 | Each dependency is justified in an authorized phase. | Install/import and dependency review. | SOURCE proposal / LOCKED |
| ARCH-002 | §22 module boundaries | `core`, `analysis`, `data`, `providers`, `reporting`, `gui` | 0–7 | No financial formulas in GUI or I/O in core. | Dependency and code review. | SOURCE / LOCKED |
| FIN-009 | §23 numerical correctness | `core` | 1 | Decimal, rounding, accrual, allocation, and invariants are specified. | Independent numerical, edge, and property tests. | OPEN conventions / LOCKED |
| REPO-001 | §§24–26 structure and AGENTS | Repository | 0 | Useful structure and scoped instructions exist when needed. | Tree and instruction consistency review. | Phase 0 authorized |
| MIG-001 | §27 `configure-cc` migration | Codex workflow | 0 | Inventory precedes adaptation; original checkout is preserved. | Inventory and preservation checks. | AUDITED; migration LOCKED |
| MIG-002 | §28 and final appendix project skills | `.agents/skills` | 0, 1, 7 | Three owner-approved skills have valid metadata and no automatic publication. | Metadata, discovery, and workflow review. | Phase 0 authorized; three manifests visible |
| PHASE-000 | §29 full Phase 0 | Repository | 0 | Install, import, GUI startup, tests, lint, types, CI, and migration checked. | Full infrastructure suite and criterion table in `harness/context/phase-00-foundation.md`. | Complete against locally verifiable criteria; hosted CI and Windows hook execution unobserved |
| PHASE-001 | §30 engine | `core` | 1 | Reproducible, independently validated calculations. | Formula, edge, property, and regression tests. | LOCKED |
| PHASE-002 | §31 desktop and persistence | `gui`, `data` | 2 | Offline interaction and durable history. | GUI, startup, and migration tests. | LOCKED |
| PHASE-003 | §32 comparison | `analysis`, `gui` | 3 | Consistent multi-scenario visualizations. | Comparison and chart regression tests. | LOCKED |
| PHASE-004 | §33 risk and optimization | `analysis` | 4 | Criteria, constraints, and uncertainty visible. | Optimization and stress regression tests. | LOCKED |
| PHASE-005 | §34 reporting | `reporting` | 5 | PDF and XLSX reconcile to core. | Export content and integrity tests. | LOCKED |
| PHASE-006 | §35 providers | `providers`, `analysis` | 6 | Historical values carry valid provenance. | Mocked provider and backtest tests. | LOCKED |
| PHASE-007 | §36 advanced features | To be decided | 7 | Exact selected scope is approved first. | Feature-specific tests after approval. | OPEN scope / LOCKED |
| HAR-001 | §37 planning documents | Harness | 0 | Goals, plans, prompts, status, decisions, and logs are discoverable. | Cross-reference and status review. | Documentation authorized |
| HAR-002 | §38 session startup | Repository policy | All | Agent reads scope, decisions, status, and local changes. | Instruction review. | APPROVED current rule |
| HAR-003 | §39 phase completion | Repository policy | All | Exact checks, limitations, and handoff are recorded before stopping. | Log and report review. | APPROVED current rule |
| HAR-004 | §40 immediate execution | Repository | 0 | Audit and authorized Phase 0 foundation performed, with evidence and exclusions recorded. | Preservation and full Phase 0 checks. | Phase 0 local implementation complete; final owner report follows |
| SEC-001 | Final appendix: skill review and independent verification | Workflow and security | 0–7 | Third-party skills are reviewed; Phase 0 has independent testing/security/maintainability review; future material financial results need independent references. | Skill audit, independent Phase 0 review, and future reference-result review. | Phase 0 review authorized; financial implementation LOCKED |

## FIN-007 atomic acceptance and verification plan

These are source requirements, not approved formulas or implemented behavior. The engine phase owns deterministic value derivation and consistency; the desktop phase owns input state and feedback. A future owner decision must specify schedule, rate, rounding, tolerance, and credit-product conventions before related calculations are implemented.

| Case | Source behavior to preserve | Planned verification |
| --- | --- | --- |
| FIN-007-A | From property price, down payment, principal, down-payment percentage, and LTV, derive a value only when all needed inputs determine one unique solution. | Equation table covering each missing member, percentage direction, zero/invalid bases, and units. |
| FIN-007-B | Rate candidates include nominal rate, bank margin, and reference-rate component; an unknown future reference observation is never invented. | Bidirectional rate-component cases and unknown-rate refusal. |
| FIN-007-C | Candidate outputs also include annuity installment under a fully specified schedule, mathematically determinable term, total repayment, interest cost, and selected cost metrics. | Independent formula/cash-flow examples; missing-convention, non-unique-term, and inconsistent-total cases. |
| FIN-007-D | Entered and computed values remain distinguishable, and computed values retain input, formula, convention, and source provenance. | Model serialization and UI origin/provenance display cases. |
| FIN-007-E | Supplied values are checked for mathematical consistency; conflicting input is never silently overwritten. | Consistent redundant-input and conflicting redundant-input cases, asserting original input preservation. |
| FIN-007-F | Underdetermined and inconsistent or overdetermined systems are detected with an explanation for why a value cannot be calculated. | Multiple unknowns, contradictory equations, and redundant consistent equations. |
| FIN-007-G | Calculation dependency cycles are prevented. | Cyclic dependency graph case terminates with an explicit error. |
| FIN-007-H | Invalid states cannot be submitted; users may lock inputs where appropriate. | GUI submit rejection and locked-value preservation under recalculation. |
| FIN-007-I | Changing an input recalculates dependent fields and updates explanations for inferred values. | GUI dependency update, stale-value removal, and explanation cases. |

## FIN-008 atomic acceptance and verification plan

No metric is implicitly interchangeable with another. The eventual payment record schema must expose dates, applied rates, balances, scheduled and actual cash flows, and allocation components sufficient to audit each result.

| Case | Source behavior to preserve | Planned verification |
| --- | --- | --- |
| FIN-008-A | Produce a mandatory installment schedule with interest and principal portions, overpayments, remaining principal after each payment, and the applied rate for every period. | Independent schedule examples, per-row allocation/balance reconciliation, rate-reset cases, and record-field audit. |
| FIN-008-B | Report total cash outflows, total interest, total financing charges, total nominal loan cost, and total repaid to the lender as distinct values. | Sum dated payment rows and separate financing charges from acquisition expenses; reconcile each named total. |
| FIN-008-C | Report contractual and effective repayment durations and total property acquisition outlay where applicable. | Early-payoff, no-overpayment, and applicable/not-applicable acquisition cases. |
| FIN-008-D | Report interest savings attributable to overpayments only against an explicit comparable baseline. | Paired cases with identical assumptions except the overpayment strategy and disclosed baseline. |
| FIN-008-E | Provide estimated effective interest rate and simplified RRSO only when their inputs, scope, and timing are defined; simplified RRSO is explicitly requested and labeled separately from legal or lender-provided RRSO. | Discounted-cash-flow independent references, request-gating, labels, and omitted-cost disclosure cases. |
| FIN-008-F | Produce contractual-style RRSO only when required assumptions and cash flows are available; never relabel a nominal-rate conversion or incomplete-cost result as full legal RRSO. | Missing mandatory cost/date refusal and scope-specific reference cash-flow cases. |
| FIN-008-G | Provide relevant financial risk metrics in the authorized risk phase with named assumptions and uncertainty. | Metric reference and stress cases in Phase 4; no invented forecast labels. |
| FIN-008-H | Every payment record carries enough information to reproduce and independently audit the calculation, including cash-flow timing conventions used for APR-related metrics. | Schema completeness, row-to-total reconciliation, independent replay, and date-shift sensitivity. |

## Classification and next batches

This grouped register covers source sections 0–40 and the final appendix; FIN-007 and FIN-008 have additional atomic cases. Before implementing other phases, break their group rows into atomic acceptance cases with owner input where behavior is materially ambiguous. Add new batches with a date and origin; keep proposals and open questions separate from approved decisions. Do not change this register's `APPROVED` state without a matching entry in `harness/decision-log.md`.
