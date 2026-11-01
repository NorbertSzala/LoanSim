# Project status

Updated: 2026-11-01.

| Item | State |
| --- | --- |
| Current authorization | The owner authorized Phase 1 on 2026-10-25 under the approved approximate monthly profile and own-funds-only recurring charges. Phase 0 and Phase 1 have met their local criteria and the required hosted CI gate for published commit `3642027b0bd5e41f47024e28bc498038615cbf7b`. Phases 2–7 are not authorized. This documentation update does not authorize Git staging, commit, or push. |
| Phase 0 | Complete against locally verifiable §29 criteria and the three-system hosted CI gate for commit `3642027`. Earlier commit `69c4dd4` failed on Ubuntu; the repaired [run `41320491886`](https://github.com/NorbertSzala/LoanSim/actions/runs/41320491886) passed on Ubuntu, macOS, and Windows. Native-window inspection and Windows live-hook execution remain unverified and are not claimed by the CI run. |
| Phase 1 | Complete against locally verifiable §30 core criteria and the three-system hosted CI gate for commit `3642027`; [run `41320491886`](https://github.com/NorbertSzala/LoanSim/actions/runs/41320491886) passed 81 tests and every required installation, import, Ruff, mypy, and build step on each system. Product GUI, persistence, providers, exports, full RRSO, actual-day accrual, and bank-specific settlement remain out of scope. |
| Phases 2–7 | LOCKED. |
| Existing source | `docs/source-requirements.md` is preserved as the primary product input. |
| Existing local changes | At the start of this status refresh, `master`, `origin/master`, and the remote `master` all pointed to `3642027`, and the tracked working tree was clean. The current documentation reconciliation is local and unstaged. The approved SessionStart hook SHA-256 is `7546a316ff33977b78fde6765954f0f685d64ce123c69c67e6556d4fc18340d7`. `VERIFY_PROGRESS_PROMPT.md`, imported third-party skills, `configure-cc/`, local environments, and caches remain ignored. |
| Completed work | Phase 0 foundation and Phase 1 core engine have local evidence and a successful hosted CI run for the exact published commit `3642027`: Ubuntu installed `libegl1`, and all three jobs passed installation, import, 81 tests, Ruff lint and format, mypy, and package build. See `build-log.md` and both phase context notes. |
| Pending | Keep Phases 2–7 locked until the owner explicitly authorizes one. Any later delivered commit, including a commit containing this documentation refresh, needs its own green hosted Ubuntu, macOS, and Windows jobs before final closure can be claimed for that new SHA. Native-window inspection and Windows live-hook execution remain unverified. |
| Open decisions | No material Phase 1 modeling question remains open. Later phases retain their own product, licensing, and distribution decisions. |

Phase 1 core implementation and local validation evidence are recorded in `context/phase-01-financial-engine.md`. The hosted CI gate was met for published commit `3642027` only. Do not advance to Phase 2 or perform Git staging, commit, or push without separate owner instructions.
