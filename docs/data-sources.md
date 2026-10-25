# Historical data and provider specification

Source: `source-requirements.md` §§19–20. Phase 6 is locked. No provider endpoint, license, or historical value is approved here.

## Required record and provenance

Each rate observation or imported row must identify the index and tenor, numerical value and units, observation date, publication date if available, effective interval, source name and retrieval/import time, source version or file hash, and any transformation. Missing, revised, proxy, reconstructed, synthetic, and forecast values must have distinct labels. The calculation input must preserve which observations and missing-data rule produced it.

## Planned behavior and tests

Offline simulation must remain possible from explicit local inputs. CSV import needs schema, encoding, decimal-separator, date, duplicate, order, and missing-value validation. Future POLSTR, WIBOR, and relevant NBP integrations require source and license verification before use; 2003 POLSTR must never be presented as actual historical observation. Test with local fixtures and mocked provider responses, including unavailable service, revisions, gaps, and reproducibility after reopening a scenario. A live provider is never required for the deterministic test suite.

## Owner decisions before implementation

Select authoritative sources and licensing terms, index definitions and observation lags, permissible historical proxies, missing-value policy, cache retention, and the interpretation of backtesting. Alternatives such as rejecting gaps versus disclosed interpolation produce different payment paths; neither is approved.
