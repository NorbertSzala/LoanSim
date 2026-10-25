# Repository audit

Audit date: 2026-10-24. This is a read-only inventory of the starting state, before the documentation changes recorded in `harness/build-log.md`.

## Git and existing files

- The main repository is on `master`, tracking `origin/master`. `LICENSE` is the only tracked file at the time of audit.
- `AGENTS.md`, `.gitignore`, `docs/`, and `skills-lock.json` are untracked. Preserve them as owner-created local work.
- `.gitignore` excludes `configure-cc/` and `.agents/`. Their contents will not appear in ordinary main-repository status output.
- `docs/source-requirements.md` is the 1,899-line primary product and workflow input. The other five existing files under `docs/` were empty at audit time.
- No application package, Python project configuration, dependency lockfile, tests, or main-repository CI workflow exists yet.
- The root instruction filename is already `AGENTS.md`; no `agents.md` migration is needed. Its original content was in Polish and is preserved in substance in the English revision made with owner approval.

## `configure-cc/` inventory

`configure-cc/` is a separate, clean Git checkout on `main`. It is a Claude Code configuration reference, not LoanSim application code. Preserve its own `.git/` and every file. Its 26 tracked files include:

| Area | Files | Assessment |
| --- | --- | --- |
| Claude instructions and skills | `CLAUDE.md`, `.claude/skills/{bootstrap,audit,audit-agents-md}/SKILL.md` | `audit-agents-md` offers useful read-only review ideas. `bootstrap` targets global `~/.claude/` and is outside LoanSim scope. Claude front matter, pre-injection commands, and tool names need adaptation. |
| Examples | `examples/claude-md/`, `examples/rules/`, `examples/skills/`, `examples/hooks/` | Some general writing and review guidance is reusable after review. The `commit` skill stages and commits; it conflicts with LoanSim's separate Git authorization rule. Hook examples use Claude's event conventions and shell pipelines; they must not be copied into Codex unchanged. |
| Guides | `guides/{hooks,multi-agent,session-management,workflows,memory-and-insights,statusline}.md` | Product-specific reference material. Do not treat Claude commands or hook behavior as Codex capabilities. |
| Tests and CI | `test/`, `Makefile`, `.github/workflows/check.yml` | Tests verify `configure-cc`, not LoanSim. Its end-to-end test may use Claude credentials and global configuration. Do not run or transplant it as a LoanSim quality gate. |

`skills-lock.json` lists five skills from `obra/superpowers` under the ignored `.agents/skills/` directory. They are local references, not newly installed or reviewed LoanSim project skills. Some instructions suggest commits; the owner rule overrides them.

## Conflicts and preservation boundaries

The existing root `AGENTS.md` authorizes only documentation and work-rule configuration at this stage. `docs/source-requirements.md` and the later repository-foundation request describe a larger Phase 0 with Python, CI, hooks, tests, and a minimal GUI shell. On 2026-10-24 the owner explicitly selected the narrower documentation-and-rules scope. The larger Phase 0 acceptance criteria remain unmet; documentation work must not be reported as completion of that phase.

Preserve `docs/source-requirements.md`, `configure-cc/`, `LICENSE`, `.gitignore`, `skills-lock.json`, and existing `.agents/` contents. No Git history-changing operation is authorized. Only the root `AGENTS.md` and the five empty `docs/` files were separately approved for editing.

## Open questions

- The exact day-count, payment allocation, rounding, rate-reset, and RRSO conventions are not specified sufficiently for implementation. See `mathematical-model.md`.
- The owner has not selected which proposed Codex hooks or subagents should be activated. See `codex-migration.md`.
- The main repository ignores `.agents/`, so future project skills would require an explicit tracking decision before they could be shared through Git.
