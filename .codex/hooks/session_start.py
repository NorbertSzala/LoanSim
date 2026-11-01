"""Give Codex a short, read-only reminder of LoanSim's phase gate."""

import json
import sys
from pathlib import Path

MAX_INPUT_BYTES = 8192
MAX_STATUS_BYTES = 16384
REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES = frozenset({"startup", "resume", "clear", "compact", "fork"})


def render_context(root: Path) -> str:
    """Read only the status field needed for a bounded advisory reminder."""
    status_path = root / "harness" / "status.md"
    with status_path.open("rb") as status_file:
        status_bytes = status_file.read(MAX_STATUS_BYTES + 1)
    if len(status_bytes) > MAX_STATUS_BYTES:
        raise ValueError("status file exceeds the hook size limit")
    status = status_bytes.decode("utf-8")
    phase_rows = [line for line in status.splitlines() if line.startswith("| Phase 0 |")]
    if len(phase_rows) != 1:
        raise ValueError("expected one Phase 0 status row")
    state = phase_rows[0].split("|")[2].strip().lower()
    if state.startswith("complete"):
        summary = "reported complete"
    elif state.startswith("in progress"):
        summary = "reported in progress"
    elif state.startswith("incomplete"):
        summary = "reported incomplete"
    else:
        summary = "requires review"
    phase_one_rows = [line for line in status.splitlines() if line.startswith("| Phase 1 |")]
    if len(phase_one_rows) > 1:
        raise ValueError("expected at most one Phase 1 status row")
    phase_reminder = "Phases 1–7 remain locked without explicit owner authorization."
    if phase_one_rows:
        phase_one_state = phase_one_rows[0].split("|")[2].strip().lower()
        if phase_one_state.startswith("in progress"):
            phase_reminder = "Phase 1 is authorized and in progress. Phases 2–7 remain locked."
        elif phase_one_state.startswith("complete"):
            phase_reminder = (
                "Phase 1 status is reported complete; verify evidence. Phases 2–7 remain locked."
            )
    return (
        "LoanSim phase reminder (advisory): read AGENTS.md, harness/status.md, "
        "and harness/decision-log.md before work. "
        f"Phase 0 status is {summary}; verify evidence before claiming completion. "
        f"{phase_reminder} "
        "This hook does not grant or enforce Git permissions."
    )


def main() -> int:
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        print("Invalid SessionStart hook input: size limit exceeded", file=sys.stderr)
        return 1
    try:
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise ValueError("input is not an object")
        if event.get("hook_event_name") != "SessionStart" or event.get("source") not in SOURCES:
            raise ValueError("unexpected hook event")
        context = render_context(REPO_ROOT)
    except (OSError, UnicodeError, ValueError, TypeError):
        print("Invalid SessionStart hook input or unavailable project status", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
