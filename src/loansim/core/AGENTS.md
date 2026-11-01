# Core calculation instructions

Phase 1 is authorized only under the owner-approved approximate monthly conventions in `docs/financial-assumptions.md` and the formulas in `docs/mathematical-model.md`. Use immutable typed inputs and `Decimal` for all money and rates. Reject floats, unsupported currencies, negative total nominal rates, historical rate gaps, and payments that cannot cover due obligations. Keep this package deterministic and independent of PySide6, databases, providers, files, and network access.

Every material formula change needs a focused failing test, an independent numerical reference, reconciliation and boundary tests, and a regression test for any discovered defect. Expose rate and fee provenance and distinguish mandatory obligations, applied extra principal, and actual cash outflow. Do not implement full RRSO or a bank-specific convention. The root `AGENTS.md` controls phase and Git authorization.
