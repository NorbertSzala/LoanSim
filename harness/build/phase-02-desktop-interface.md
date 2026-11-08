# Phase 2 — Desktop interface and persistence

Status: **LOCAL §31 CHECKS PASSED AFTER INDEPENDENT AUDIT REPAIRS; HOSTED CI FOR A DELIVERED COMMIT PENDING** under the owner's 2026-11-01 authorization and subsequent repair request. The owner's `1A, 2A, 3A` choices are in `harness/decision-log.md`. Source: `docs/source-requirements.md` §§9, 11, 16, 31; `docs/ui-specification.md`.

## Objective, scope, and non-goals

Build an offline PySide6 single-scenario workflow with dynamic derived fields, validation feedback, results, local SQLite history, reopen/duplicate flows, and basic single-scenario charts. Keep financial rules in `core`. Exclude multi-scenario comparison, optimization, providers, and exports.

## Dependencies and milestones

Depends on the verified Phase 1 engine and the approved Polish form, complete snapshot, explicit deletion, and Qt-only chart choices. Milestones: (1) input and result interaction; (2) versioned persistence with reproducible snapshots; (3) history and single-scenario charts; (4) offline and recovery verification. No Phase 3 comparison entry point is implemented.

## Expected files and tests

Implementation adds `src/loansim/gui/` form, results, history, worker, and chart views; `src/loansim/data/` snapshot codec and SQLite repository with `data/AGENTS.md`; and offscreen GUI/integration tests. The audit repairs add background schedule validation, stale-value clearing, field-linked errors, complete result columns, saved derivation display, duplicate-version preservation, protection against double or late saves, preservation of an older result's engine version on resave, latest-request-wins history opening, stale-open-failure suppression, metadata-only edits without recalculation or provenance loss, and restoration failure without form, editability, or validation loss. Local checks cover FIN-007 origin, locks, errors, recalculation, and refusal cases; history round trips, migration, integrity, failed writes, timestamps, nonblocking behavior, and offline startup. Evidence is recorded in `harness/context/phase-02-desktop-interface.md` and `harness/build-log.md`. Native-window inspection and cross-platform hosted CI remain unverified.

## Acceptance, risks, and owner questions

Acceptance requires meaningful single-scenario interactions and reproducible saved results offline. Risks: lost inputs, stale derivations, corrupt migrations, inaccessible error feedback. The owner resolved workflow, validation style, snapshot versus recalculation, deletion, and chart presentation on 2026-11-01. Final closure still requires a green hosted Ubuntu, macOS, and Windows run for the exact delivered commit. The separately approved `SessionStart` hook still describes Phases 2–7 as locked until a new revision is reviewed and explicitly approved; it is advisory and must not be used as the current authorization source.
