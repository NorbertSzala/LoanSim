# Data instructions

Keep SQLite and serialization outside `core`. Preserve exact Decimal values, original inputs, derived provenance, source dates, financial conventions, engine version, and result snapshots. Use transactional, versioned migrations; never silently discard old records. Reject unknown formats and newer schema versions. Test real database round trips, migrations, failed writes, and deletion without network access. Root `AGENTS.md` controls phase and Git authorization.
