# Reporting and export specification

Source: `source-requirements.md` §§17–18 and 34. Phase 5 is locked. No exporter exists in Phase 0.

## Required outputs

XLSX and PDF must show scenario identity, inputs, assumptions and conventions, payment schedule, cost totals, comparisons where applicable, source provenance, methodology, and limitations. Use clear financial units and currency. A generated XLSX formula is not evidence that spreadsheet software recalculated it. Reports must not relabel simplified RRSO as legal RRSO or omit material cost scope.

## Verification plan

Open and parse representative files; inspect sheet/page structure, displayed values, formulas where used, dates, Unicode and Polish characters, and currency formatting. Independently reconcile exported totals and representative payment rows with validated engine results. Visually inspect representative PDFs. Test partial or failed writes and avoid replacing user files without an explicit user action.

## Owner decisions before implementation

Approve report detail level, templates, chart inclusion, file replacement behavior, required disclosures, and PDF library/font license. These choices affect interpretability, compatibility, and distribution obligations.
