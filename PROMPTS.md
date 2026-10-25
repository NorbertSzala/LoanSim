# Reusable prompts

These templates help transfer context. None grants permission beyond an explicit owner instruction. Replace bracketed text before use.

## Orientation

> Read `AGENTS.md`, `harness/status.md`, the relevant approved phase plan, recent decisions, and Git status. Summarize the authorized scope, local changes, and unresolved questions. Do not modify files.

## Read-only architecture review

> Review [topic] against `docs/source-requirements.md` and `docs/architecture.md`. Present viable alternatives, consequences, and a recommendation. Do not implement or mark a proposal approved.

## Start an authorized phase

> I explicitly authorize [phase and bounded scope]. Read `AGENTS.md`, `harness/status.md`, the relevant plan, and decisions. Present the file plan first. Work only within this phase, validate each coherent change, report results, and stop. This instruction does not authorize Git staging, commit, or push unless I explicitly add those permissions.

## Verify or review

> Perform read-only verification/review of [files or behavior]. For a previous phase or agent delivery, consult the owner-provided local `VERIFY_PROGRESS_PROMPT.md` checklist if present. Run the applicable checks, report exact commands, exit codes, results, and unverified areas. Do not claim a phase is complete solely because a subset passes.

## Handoff

> Update the approved documentation and logs for [completed task] with observed checks and outstanding decisions. Report the current authorization state and stop.

## Separately authorized Git actions

> I authorize `git add` for [exact files] after inspection and verification. Leave the files staged and uncommitted.

> I explicitly order `git commit` for [exact staged files] with message [exact message], after reviewing the staged diff and fresh checks. Do not push.

> I separately authorize pushing [exact existing commit and destination]. Verify the intended remote and ref before pushing. Do not create another commit or merge.
