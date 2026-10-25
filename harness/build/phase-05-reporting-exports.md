# Phase 5 — Reporting and exports

Status: **LOCKED**. Source: `docs/source-requirements.md` §§17–18, 34; `docs/export-specification.md`.

## Objective, scope, and non-goals

Create XLSX and PDF reports with scenarios, schedules, charts where approved, totals, assumptions, methodology, provenance, and limitations. Export validated results; do not recalculate loans independently in reporting. Exclude data-provider work.

## Dependencies and milestones

Depends on validated engine and comparison outputs and approved report detail/license choices. Milestones: (1) report schema and representative fixtures; (2) XLSX; (3) PDF; (4) cross-format reconciliation and visual review.

## Expected files and tests

Expected future `src/loansim/reporting/` exporters with `reporting/AGENTS.md` and file-integrity tests. Parse/open artifacts; inspect formulas, values, dates, sheets/pages, Unicode, currency units, source notes, failed writes, and exact reconciliation to engine totals.

## Acceptance, risks, and owner questions

Acceptance requires both formats, readable disclosures, file integrity, and verified numeric equality to engine output. Risks: spreadsheet recalc assumptions, font licensing, rounded display discrepancies. Owner decisions: layout, detail level, PDF library/font, overwrite behavior, required legal wording.
