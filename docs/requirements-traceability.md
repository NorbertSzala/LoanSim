# Requirements traceability register

This register classifies the **numbered source sections and major subsections**, rather than each individual bullet, in `source-requirements.md`. The source remains unchanged. `SOURCE` means owner-provided product or process scope, **not** approval to implement a locked phase or a missing convention. `OPEN` means an owner decision is needed. `APPROVED` refers only to explicit decisions recorded in `harness/decision-log.md`. Acceptance and test columns describe future evidence, not tests already run.

| ID | Original source | Target area | Phase | Acceptance criterion | Planned verification | Status |
| --- | --- | --- | --- | --- | --- | --- |
| GOV-001 | §§0–6: role, decisions, phases, Git, testing, communication | Repository policy | All | Phase boundaries and human gates are explicit. | Instruction/status consistency review. | APPROVED current rule |
| PRD-001 | §7: offline desktop vision and result provenance | Product | 2–7 | Core use works offline; results disclose inputs and assumptions. | Offline smoke and result audit. | SOURCE / LOCKED |
| FIN-001 | §8 property information | `core` inputs | 1 | Property, down payment, principal, LTV, currency, and costs are represented. | Model validation and equation tests. | Phase 1 core COMPLETE locally |
| FIN-002 | §8 loan parameters | `core` inputs | 1 | Dates, term, frequency, schedule type, and charges are explicit. | Boundary and date tests. | Phase 1 core COMPLETE locally |
| FIN-003 | §8 rate configuration | `core`, `providers` | 1, 6 | Fixed, periodically fixed, and variable paths retain index and dates. | Reset and provenance tests. | Phase 1 core COMPLETE locally; providers LOCKED |
| FIN-004 | §8 early repayment | `core` | 1 | Supported schedules and responses distinguish obligation from actual outflow. | Cash-flow equivalence and fee tests. | Phase 1 core COMPLETE locally |
| FIN-005 | §8 fees and expenses | `core` | 1 | Financing charges and acquisition expenses stay separate. | Cost reconciliation tests. | Phase 1 core COMPLETE locally |
| FIN-006 | §8 RKM and special programs | `core` extension | 7 | Rules are dated and verified before any eligibility result. | Program-rule cases against approved source. | OPEN detail / LOCKED |
| FIN-007 | §9 missing-value calculation | `core`, `gui` | 1, 2 | All §9 candidate values and eleven behavior rules are mapped below. | FIN-007 case matrix below. | Phase 1 core COMPLETE locally; GUI LOCKED |
| FIN-008 | §10 simulation outputs | `core`, `analysis`, `gui` | 1–4; fuller RRSO later | Every §10 output and APR/RRSO disclosure rule is mapped below, with the 2026-10-25 Phase 1 metric limit. | FIN-008 case matrix below. | Phase 1 core COMPLETE locally; later scopes LOCKED |
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
| FIN-009 | §23 numerical correctness | `core` | 1 | Decimal, rounding, accrual, allocation, and invariants are specified. | Independent numerical, edge, and property tests. | Conventions APPROVED; Phase 1 implementation COMPLETE locally |
| REPO-001 | §§24–26 structure and AGENTS | Repository | 0 | Useful structure and scoped instructions exist when needed. | Tree and instruction consistency review. | Phase 0 authorized |
| MIG-001 | §27 `configure-cc` migration | Codex workflow | 0 | Inventory precedes adaptation; original checkout is preserved. | Inventory and preservation checks. | AUDITED; migration LOCKED |
| MIG-002 | §28 and final appendix project skills | `.agents/skills` | 0, 1, 7 | Three owner-approved skills have valid metadata and no automatic publication. | Metadata, discovery, and workflow review. | Phase 0 authorized; three manifests visible |
| PHASE-000 | §29 full Phase 0 | Repository | 0 | Install, import, GUI startup, tests, lint, types, CI, and migration checked. | Local infrastructure suite and criterion table in `harness/context/phase-00-foundation.md`; hosted run `41320491886` passed Ubuntu/macOS/Windows jobs for published commit `3642027`. | Local criteria and hosted CI gate met for `3642027`; later delivered commits need their own green run |
| PHASE-001 | §30 engine | `core` | 1 | Reproducible, independently validated calculations under the approved approximate monthly model. | Formula, edge, property, and regression tests plus hosted run `41320491886`, with all three jobs green for published commit `3642027`. | Core criteria and hosted CI gate met for `3642027`; Phase 2 LOCKED |
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
| SEC-001 | Final appendix: skill review and independent verification | Workflow and security | 0–7 | Third-party skills are reviewed; Phase 0 has independent testing/security/maintainability review; future material financial results need independent references. | Skill audit, independent Phase 0 review, and Phase 1 reference-result review. | Phase 1 numerical references verified locally; later scopes LOCKED |

## FIN-007 atomic acceptance and verification plan

These are source requirements with Phase 1 core implementation complete against local criteria. The engine owns deterministic value derivation and consistency; the locked desktop phase owns input state and feedback. The owner approved an approximate equal-monthly-period model and detailed conventions on 2026-10-25. The owner also selected own-funds-only recurring charges for Phase 1; a financed recurring charge fails validation.

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

No metric is implicitly interchangeable with another. The eventual payment record schema must expose dates, applied rates, balances, scheduled and actual cash flows, and allocation components sufficient to audit each result. The approved Phase 1 metric is simplified effective annual interest under monthly compounding, clearly separate from RRSO; fuller discounted-cash-flow RRSO is deferred.

| Case | Source behavior to preserve | Planned verification |
| --- | --- | --- |
| FIN-008-A | Produce a mandatory installment schedule with interest and principal portions, overpayments, remaining principal after each payment, and the applied rate for every period. | Independent schedule examples, per-row allocation/balance reconciliation, rate-reset cases, and record-field audit. |
| FIN-008-B | Report total cash outflows, total interest, total financing charges, total nominal loan cost, and total repaid to the lender as distinct values. | Sum dated payment rows and separate financing charges from acquisition expenses; reconcile each named total. |
| FIN-008-C | Report contractual and effective repayment durations and total property acquisition outlay where applicable. | Early-payoff, no-overpayment, and applicable/not-applicable acquisition cases. |
| FIN-008-D | Report interest savings attributable to overpayments only against an explicit comparable baseline. | Paired cases with identical assumptions except the overpayment strategy and disclosed baseline. |
| FIN-008-E | In Phase 1 provide annual nominal interest and simplified effective annual interest under monthly compounding, labeled separately from official RRSO. The source's simplified RRSO request belongs to a later, separately specified scope. | Independent fixed-rate conversion examples, zero-rate case, variable-path labeling, and an assertion that no RRSO label appears in Phase 1. Later request-gating and discounted-cash-flow references need a new authorization. |
| FIN-008-F | Contractual-style RRSO from the source is deferred beyond Phase 1. Never relabel a nominal-rate conversion or incomplete-cost result as full legal RRSO. | In Phase 1, verify refusal or absence of a full-RRSO result. In a later authorized scope, require complete-cost/date reference cash flows. |
| FIN-008-G | Provide relevant financial risk metrics in the authorized risk phase with named assumptions and uncertainty. | Metric reference and stress cases in Phase 4; no invented forecast labels. |
| FIN-008-H | Every payment record carries enough information to reproduce and independently audit the calculation. Phase 1 dates label equal model periods; a later RRSO scope will need dated cash-flow timing conventions. | Schema completeness, row-to-total reconciliation, and independent replay in Phase 1; date-shift sensitivity when a dated metric is authorized. |

## 2026-10-25 owner-approved Phase 1 profile

The later owner decision selects a general, approximate simulator with equal monthly periods, nominal annual rate divided by 12, `Decimal`, two-decimal `ROUND_HALF_UP` settlement, once-per-period interest rounding, fixed/periodically fixed/variable paths, disclosed future-rate continuation, annuity and declining schedules, selected overpayments, separated costs, and simplified effective annual interest. `docs/financial-assumptions.md` records the approved choices, including the subsequent own-funds-only recurring-charge rule. A separate owner reply on 2026-10-25 authorized Phase 1 implementation and accepted the seven detailed recommendations in `harness/decision-log.md`. Deferred source requirements remain in this register. No Git staging, commit, push, or later phase was authorized.

## Classification and next batches

This grouped register covers source sections 0–40 and the final appendix; FIN-007 and FIN-008 have additional atomic cases. Before implementing other phases, break their group rows into atomic acceptance cases with owner input where behavior is materially ambiguous. Add new batches with a date and origin; keep proposals and open questions separate from approved decisions. Do not change this register's `APPROVED` state without a matching entry in `harness/decision-log.md`.
