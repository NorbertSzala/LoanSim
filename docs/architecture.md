# Planned architecture

This map derives from `source-requirements.md` sections 21–26. Phase 0 implements only the package entry point and a presentation-only GUI startup shell. Other boundaries remain planned interfaces, not implemented modules.

| Planned boundary | Responsibility | Must not own |
| --- | --- | --- |
| `core` | Typed financial inputs and deterministic repayment, interest, overpayment, cost, and APR-related calculations. | GUI, database, provider I/O, or invented conventions. |
| `analysis` | Scenario comparison, transparent risk metrics, sensitivity, break-even, and constrained optimization. | Hidden financial formulas or opaque recommendations. |
| `data` | SQLite persistence, schema versions, simulation history, and reproducible snapshots. | Financial business rules. |
| `providers` | Verified external or imported rate series with source, dates, units, and missing-data policies. | GUI state or fabricated observations. |
| `reporting` | PDF and XLSX presentation of validated engine results with provenance. | Independent recalculation of loan formulas. |
| `gui` | PySide6 input, validation feedback, charts, and user interactions. | Financial formulas or blocking I/O on the main thread. |

The intended dependency direction is `gui`, `reporting`, and `analysis` consuming validated `core` results; `data` and `providers` provide explicit I/O boundaries. The exact package interfaces and dependency library choices are future architectural decisions. The preferred stack in the source is a proposal, not permission to install every library.

Create nested `AGENTS.md` files when their directories are introduced in an authorized programming phase. Phase 0 introduces `gui` and `tests` instructions. The root policy applies to every module; nested guidance adds only domain-specific tests and invariants.

Open issues include input model boundaries, reproducible calculation versioning, GUI/background work strategy, and provider licensing. Record trade-offs and ask the owner before choices with material consequences.
