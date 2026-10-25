---
name: release-check
description: Check a LoanSim release candidate or final delivery only after the owner explicitly authorizes that release scope; report evidence without publishing.
---

# Release check

Read `AGENTS.md`, `harness/status.md`, the authorized release scope, and the relevant phase acceptance criteria. This workflow reports readiness; it grants no permission to distribute software.

1. Run the complete applicable automated tests, lint, type checks, package installation/build verification, and GUI launch checks in representative supported environments. Record exact commands, exit codes, and unresolved failures.
2. Check documentation, assumptions, version and dependency metadata, and license/distribution obligations against the approved release scope.
3. Where exports exist, open and inspect PDF and XLSX artifacts and reconcile their values to validated engine results.
4. Review unresolved defects and prepare a release note draft that distinguishes verified behavior from limitations.

Do not create a commit, tag, push, PR, package publication, or release without separate explicit owner authorization for each applicable action. Do not waive a failing check or claim an unexecuted check passed.
