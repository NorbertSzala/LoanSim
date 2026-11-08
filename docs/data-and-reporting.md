# Data, history, providers, and reporting

Source: `source-requirements.md` sections 16–20. Phase 2 implements local SQLite scenario history. Providers and exporters remain locked later-phase scope.

## Persistence

The Phase 2 SQLite history retains a UUID, name, color, notes, UTC-aware creation and modification times, the exact original form state and locks, derived-value explanations, validated terms, rate and overpayment assumptions, classified charges, the convention ID, package version, and the complete result snapshot. The JSON codec allowlists core types and preserves `Decimal` and date values exactly. Schema version 2 migrates version 1 transactionally, preserves previous rows, and adds an engine-version field and SHA-256 snapshot integrity value. Newer schema versions are rejected. Reopen shows the saved result without silent recalculation; resaving an unchanged old result preserves its engine version. A saved form state that cannot be restored leaves the current form intact and produces a visible error without deleting the record. Duplicate creates a new ID; delete requires confirmation. No automatic retention cleanup occurs. Comparison and saved comparisons remain Phase 3 scope.

Edits to only the scenario name, color, or notes update both the SQLite metadata columns and the original-input metadata inside the snapshot. They retain the historical result, derived provenance, and engine version. Financial input edits require a fresh calculation before saving a replacement result.

## XLSX and PDF

Both exports are required in the reporting phase. XLSX should contain a readable summary, assumptions, repayment schedule, cost and scenario comparisons, provenance, methodology, and limitations. Use `openpyxl` unless an alternative is justified and approved. Validate workbook structure and exported computed values; writing formulas alone does not prove recalculation.

PDF should contain readable financial tables, charts where relevant, assumptions, provenance, limitations, Unicode and Polish characters, and consistent financial formatting. Choose a maintained library when implementation is authorized. Do not include unlicensed fonts. Parse and visually inspect representative output where practical, and reconcile financial totals with the engine.

## Reference-rate data and historical analysis

Future providers may support POLSTR, WIBOR, relevant NBP data, and local CSV, subject to source and licensing verification. Each series needs index definition, source, units, observation and publication dates when available, missing-value policy, and data version. Core simulation must work offline. Historical observations, reconstructed indices, proxies, synthetic paths, and forecasts must remain distinctly labeled. Modern POLSTR observations must never be represented as actual 2003 data.

## Open decisions

Phase 2 retention, deletion, snapshot, and chart choices were approved on 2026-11-01. Supported export detail, provider licenses and access methods, permitted historical proxies, and backtesting interpretation remain open for their later phases.
