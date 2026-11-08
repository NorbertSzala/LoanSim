# Development and requirements workflow

The root `AGENTS.md` is the enforceable repository instruction file. `harness/status.md` records the active authorization. `PLANS.md` is a roadmap, not permission to implement. Phase 0 and Phase 1 met their local and hosted CI criteria for published commit `3642027`; the owner authorized Phase 2 on 2026-11-01. Phases 3–7 remain locked. Phase 2 final closure requires a green hosted three-system CI run for its exact delivered commit.

## Start a session

Read root and applicable nested instructions, status, approved decisions, the relevant phase description, and Git status. Identify pre-existing uncommitted work. Read only domain documents needed for the requested task. If the phase or scope is unclear, ask before affecting that path.

For an independent audit of a previous phase or agent delivery, read the owner-provided local `../VERIFY_PROGRESS_PROMPT.md` after the root instructions if it exists. The owner keeps this optional checklist Git-ignored; a fresh checkout may not contain it. Treat it as review guidance, not as permission to implement changes or perform Git operations.

## Receive requirements in batches

1. Record each new owner message with date and source in `requirements-traceability.md` or a linked, owner-approved addendum. Do not silently rewrite `source-requirements.md`.
2. Classify each item as an explicitly approved decision, source-level requirement, proposal, or open question. Link the target module, phase, acceptance evidence, and planned verification.
3. Identify conflicts with earlier requirements or phase boundaries and present alternatives with consequences. Do not infer approval from a draft.
4. Update `PLANS.md` and `harness/status.md` only after the owner authorizes a scope change. Record the decision in `harness/decision-log.md`.

## Make and verify changes

Present a plan and file list before editing. Make coherent, reviewable changes. Run targeted checks after each change group; investigate failures and re-run. Before reporting completion, run all applicable checks, inspect outputs, verify preservation of owner files, inspect read-only Git status, and record exact results in `harness/build-log.md`. Phase 0 startup checks and Phase 1 financial tests are applicable to the current repository; export tests require a later authorized phase.

## Finish a phase

Report actual deliverables, checks, limitations, unresolved decisions, and Git status in Polish, then stop. No phase advances automatically. Stage only exact inspected files when the owner explicitly authorizes `git add`; commit only when explicitly ordered after staged-diff review and fresh checks; push only with separate explicit authorization. Branching, merging, tagging, and PR actions also require explicit authorization. Neither a skill nor a subagent may change these requirements or automate commits or pushes.
