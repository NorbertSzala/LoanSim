# Owner decision log

Record approvals only after they are explicitly received. A proposal is not an approved decision.

| Date | Decision | Alternatives and consequence | Owner approval | Affected area |
| --- | --- | --- | --- | --- |
| 2026-10-24 | Current work is limited to documentation and work-rule configuration. | The broader Phase 0 would include scripts, tests, Python/CI setup, and a GUI shell; those remain unauthorized. | Explicit response in this task. | Entire repository and phase gating. |
| 2026-10-24 | Translate and update the existing root `AGENTS.md` and fill the five empty domain documents, preserving the original restrictions. | Leaving them unchanged would prevent the requested English instruction and documentation handoff. | Explicit response in this task. | `AGENTS.md`; five existing `docs/` files. |
| 2026-10-24 | Authorize the remaining Phase 0 foundation under source §29, with Phase 1 and history-changing Git operations excluded. | The prior documentation-only boundary left installation, startup, tests, and CI unimplemented. This authorization permits those foundation deliverables but no financial or product features. | Explicit owner message in this task. | Phase 0 software, configuration, tests, CI, and harness. |
| 2026-10-24 | Track only the two new LoanSim project skills; keep five imported third-party skills local and ignored. | Tracking all imported skills would require a broader audit and ongoing maintenance; the small allowlist gives a reproducible project configuration. | Explicit owner response in this task. | `.gitignore`, `.agents/skills/`, migration documentation. |
| 2026-10-24 | Set the Phase 0 minimum Python version to 3.11. | Python 3.12+ would narrow supported environments; 3.11+ retains broader compatibility while requiring a newer interpreter than the local system 3.9.6. | Explicit owner response in this task. | `pyproject.toml`, lockfile, CI, installation checks. |

No financial or mathematical modeling convention has been approved by these decisions.

## Later owner authorization on 2026-10-24

The following explicit owner message supersedes the older documentation-only and two-skill limits above. The older rows remain as history, not current restrictions.

| Date | Decision | Alternatives and consequence | Owner approval | Affected area |
| --- | --- | --- | --- | --- |
| 2026-10-24 | Complete remaining Phase 0, create and make Git-visible all three project skills, and select a small useful set of Codex hooks. | Leaving the earlier two-skill/no-hook state would omit the final source appendix and owner-requested configuration. Hooks still require verified trust and execution before an operational claim. | Explicit current owner message. | Phase 0, `.agents/skills/`, `.codex/`, documentation and tests. |
| 2026-10-24 | Authorize `git add` only for exact inspected and verified Phase 0 files; leave them staged and uncommitted. A later explicit commit order permits that commit after staged-diff review and fresh checks. Push requires a separate explicit order. | Without staging, the handoff omits the owner-requested index state; automatic commit or push would remove the owner's control. | Explicit current owner message. | Git workflow, `AGENTS.md`, work rules. |
| 2026-10-25 | Trust the reviewed project `SessionStart` hook definition in Codex and try an actual run. | Leaving the hook installed but inactive would prevent an operational claim; trust applies to the exact reviewed definition and does not grant Git or phase authority. | Explicit owner reply: “Tak, zatwierdź ten hook”. | `.codex/hooks.json`, `.codex/hooks/session_start.py`, local Codex trust state. |
| 2026-10-25 | Treat `VERIFY_PROGRESS_PROMPT.md` as an owner-provided LoanSim audit checklist and make it discoverable to agents as project material. | Leaving it as an unexplained local file makes an intended audit procedure appear extraneous; identifying it in project instructions and handoffs preserves its review-only purpose. This decision does not itself authorize Git staging, a commit, or a push. | Explicit owner instruction in the current task. | `VERIFY_PROGRESS_PROMPT.md`, root instructions, prompts, workflow, and Phase 0 handoff. |
| 2026-10-25 | Keep `VERIFY_PROGRESS_PROMPT.md` local and Git-ignored; stage the other current changes and request their publication and merge on GitHub. | Ignoring the checklist preserves the owner's local copy but means fresh checkouts and source distributions cannot use it. The only remote branch observed is `master`, so there is no existing source branch to merge. A commit still needs a separate explicit order under `AGENTS.md`. | Explicit owner instruction in the current task. | `.gitignore`, audit-checklist references, Phase 0 handoff, and Git workflow. |
| 2026-10-25 | Make the necessary shared project files available to future agents starting from a fresh checkout. | Ignoring all Markdown would omit repository instructions, source requirements, decisions, plans, and the status file required by the shared hook. Keep the specifically designated local audit checklist and imported skills ignored; stage the reviewed Phase 0 project files under the prior staging authorization. This decision does not authorize a commit or push. | Explicit owner request to make future agent startup easy. | `.gitignore`, `README.md`, Phase 0 handoff, and Git index. |

No future phase or financial convention is approved by the later message.
