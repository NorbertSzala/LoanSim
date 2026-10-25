# Phase 2 — Desktop interface and persistence

Status: **LOCKED**. Source: `docs/source-requirements.md` §§9, 11, 16, 31; `docs/ui-specification.md`.

## Objective, scope, and non-goals

Build an offline PySide6 single-scenario workflow with dynamic derived fields, validation feedback, results, local SQLite history, reopen/duplicate flows, and basic single-scenario charts. Keep financial rules in `core`. Exclude multi-scenario comparison, optimization, providers, and exports.

## Dependencies and milestones

Depends on a verified Phase 1 engine and owner-approved UI, storage, and retention choices. Milestones: (1) input and result interaction; (2) versioned persistence with reproducible snapshots; (3) history and single-scenario charts; (4) offline and recovery verification.

## Expected files and tests

Expected future `src/loansim/gui/` views and `src/loansim/data/` repository/migration modules with `data/AGENTS.md`, plus GUI and integration tests. Test FIN-007 input origin, locks, errors, recalculation, and refusal cases; history round trips, old-version migrations, failed writes, timestamps, keyboard access, nonblocking behavior, and offline startup.

## Acceptance, risks, and owner questions

Acceptance requires meaningful single-scenario interactions and reproducible saved results offline. Risks: lost inputs, stale derivations, corrupt migrations, inaccessible error feedback. Owner decisions: workflow, validation style, schema/version strategy, deletion and recovery semantics, and chart presentation.
