# Phase 7 — Advanced features and distribution

Status: **LOCKED; exact scope undecided**. Source: `docs/source-requirements.md` §36.

## Objective, scope, and non-goals

Candidate work includes refinancing, inflation-adjusted cost, present value, Monte Carlo rates, liquidity planning, saving-versus-overpaying, templates, localization, installers, and release automation. No candidate is approved for implementation by this plan. Avoid treating exploratory simulation as a prediction.

## Dependencies and milestones

Depends on owner selection of a bounded subset and the relevant earlier verified phases. Once selected: (1) decision and measurable spec; (2) independent reference or usability cases; (3) implementation; (4) platform/release verification where applicable.

## Expected files and tests

Exact files depend on the chosen feature. Tests must cover its assumptions, reproducibility, edge cases, and failure modes. Distribution work would add platform-specific packaging and installation checks only after target platforms and license obligations are approved.

## Acceptance, risks, and owner questions

Acceptance criteria cannot be finalized before feature selection; Phase 7 remains incomplete by design. Risks: open-ended scope, false precision, platform incompatibility, and release obligations. Owner must approve exact feature set, target systems, numerical conventions, and release process before work begins.
