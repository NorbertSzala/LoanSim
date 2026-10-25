# Phase 6 — Historical data and providers

Status: **LOCKED**. Source: `docs/source-requirements.md` §§19–20, 35; `docs/data-sources.md`.

## Objective, scope, and non-goals

Add local CSV import, verified rate-provider interfaces, offline cache, and reproducible backtesting with explicit observation/proxy/forecast provenance. Do not fabricate historical data or require a live service for ordinary simulation.

## Dependencies and milestones

Depends on rate-path engine support, persistence, and approved source licenses/index conventions. Milestones: (1) source/legal verification and data contract; (2) CSV and local fixtures; (3) approved providers; (4) backtesting and reproducibility checks.

## Expected files and tests

Expected future `src/loansim/providers/` modules with `providers/AGENTS.md`, analysis backtesting module, local fixtures, and mocked integration tests. Test invalid CSV, missing/revised observations, source outages, offline fallback, cache versioning, data provenance, and no false historical POLSTR claims.

## Acceptance, risks, and owner questions

Acceptance requires traceable observations and repeatable backtests without invented values. Risks: licensing breaches, mislabeled proxies, silent gaps. Owner decisions: provider sources, access rights, index and reset definitions, historical proxies, gap rules, and cache retention.
