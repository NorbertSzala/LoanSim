# Planned architecture

This map derives from `source-requirements.md` sections 21–26. Phase 0 implemented the package entry point, Phase 1 added a deterministic I/O-free `core`, and Phase 2 is authorized to add the single-scenario `gui` and local SQLite `data` boundaries. Analysis, providers, and reporting remain planned interfaces.

| Planned boundary | Responsibility | Must not own |
| --- | --- | --- |
| `core` | Typed financial inputs and deterministic repayment, interest, overpayment, cost, and simplified effective-rate calculations under explicit conventions. | GUI, database, provider I/O, full RRSO, or invented conventions. |
| `analysis` | Scenario comparison, transparent risk metrics, sensitivity, break-even, and constrained optimization. | Hidden financial formulas or opaque recommendations. |
| `data` | SQLite persistence, schema versions, simulation history, exact input/result snapshots, and integrity checks. | Financial business rules. |
| `providers` | Verified external or imported rate series with source, dates, units, and missing-data policies. | GUI state or fabricated observations. |
| `reporting` | PDF and XLSX presentation of validated engine results with provenance. | Independent recalculation of loan formulas. |
| `gui` | PySide6 input, validation feedback, charts, and user interactions. | Financial formulas or blocking I/O on the main thread. |

The intended dependency direction is `gui`, `reporting`, and `analysis` consuming validated `core` results; `data` and `providers` provide explicit I/O boundaries. The exact package interfaces and dependency library choices are future architectural decisions. The preferred stack in the source is a proposal, not permission to install every library.

Nested `AGENTS.md` files cover `gui`, `tests`, `core`, and the Phase 2 `data` package. The root policy applies to every module; nested guidance adds only domain-specific tests and invariants.

Phase 2 uses `QThreadPool` for calculation and database operations while `core` remains independent of Qt and I/O. Snapshots retain the engine's calculation-convention identifier. Provider licensing and later analysis/reporting boundaries remain open for their authorized phases. Record trade-offs and ask the owner before choices with material consequences.
