# Project status

Updated: 2026-10-25.

| Item | State |
| --- | --- |
| Current authorization | Phase 0 foundation was authorized on 2026-10-24, including three project skills, one justified hook, and exact-file `git add` after review. The owner trusted the exact hook on 2026-10-25, directed that the local audit prompt remain ignored, and requested a usable shared handoff for future agents. No later phase is authorized. A commit still needs an explicit order; the merge path is unresolved because only remote `master` exists. |
| Phase 0 | Complete against locally verifiable §29 criteria. Python 3.11 clean installation, import, offscreen startup and rendered window, nine tests, Ruff, mypy, package build, documentation/skill checks, CI YAML checks, and actual local Codex hook execution passed. Hosted GitHub Actions and the Windows hook override have not run. |
| Phases 1–7 | LOCKED. |
| Existing source | `docs/source-requirements.md` is preserved as the primary product input. |
| Existing local changes | The 52 Phase 0 project files are staged and uncommitted, including shared Markdown instructions and plans, three project skills, the hook, and the startup guide. `VERIFY_PROGRESS_PROMPT.md` remains local, unchanged, and Git-ignored. Five imported third-party skill directories, `configure-cc/`, local environments, and caches remain ignored and unstaged. These staged files will reach a fresh checkout only after an authorized commit and publication. No commit or push has yet been performed. |
| Completed work | Foundational Python package and Qt startup shell, dev tooling and lockfile, cross-platform CI definition, three project skills, one trusted and locally executed advisory `SessionStart` hook, nested GUI/test rules, FIN-007/008 acceptance cases, future phase plans, domain specifications, and a README start checklist. The owner has identified `VERIFY_PROGRESS_PROMPT.md` as a local, read-only audit checklist; its content is preserved and it is excluded from source distributions. See `build-log.md` and `context/phase-00-foundation.md` for evidence. |
| Pending | Explicit commit order and GitHub integration path; hosted CI after publication; Windows hook execution and native-window inspection on applicable environments. |
| Open decisions | All financial conventions and detailed product behavior in future-phase documents; licensing and target-platform review before distribution. |

Next action: review the refreshed staged diff and settle the commit and GitHub integration path. Phase 1 remains locked until an explicit bounded authorization and the required financial decisions. Do not infer permission from the roadmap.
