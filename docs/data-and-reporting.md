# Data, history, providers, and reporting

Source: `source-requirements.md` sections 16–20. This is future product scope; no database, provider, or exporter exists yet.

## Persistence

The planned local SQLite history retains simulation identity, names, colors, timezone-aware creation and modification times, original and derived inputs, conventions, rate and overpayment assumptions, data provenance, engine version, notes, and reproducible results or references. Reopen, duplicate, compare, and explicit delete flows require versioned migrations and data-integrity tests. Migration behavior must preserve previous simulation inputs.

## XLSX and PDF

Both exports are required in the reporting phase. XLSX should contain a readable summary, assumptions, repayment schedule, cost and scenario comparisons, provenance, methodology, and limitations. Use `openpyxl` unless an alternative is justified and approved. Validate workbook structure and exported computed values; writing formulas alone does not prove recalculation.

PDF should contain readable financial tables, charts where relevant, assumptions, provenance, limitations, Unicode and Polish characters, and consistent financial formatting. Choose a maintained library when implementation is authorized. Do not include unlicensed fonts. Parse and visually inspect representative output where practical, and reconcile financial totals with the engine.

## Reference-rate data and historical analysis

Future providers may support POLSTR, WIBOR, relevant NBP data, and local CSV, subject to source and licensing verification. Each series needs index definition, source, units, observation and publication dates when available, missing-value policy, and data version. Core simulation must work offline. Historical observations, reconstructed indices, proxies, synthetic paths, and forecasts must remain distinctly labeled. Modern POLSTR observations must never be represented as actual 2003 data.

## Open decisions

Retention and deletion semantics, exact schema, supported export detail, provider licenses and access methods, permitted historical proxies, and backtesting interpretation need owner review before implementation.
