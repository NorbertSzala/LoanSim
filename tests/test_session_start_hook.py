"""Isolated contract checks for the optional Codex session hook."""

import json
import runpy
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".codex" / "hooks" / "session_start.py"


def _invoke(payload: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        check=False,
        text=True,
        timeout=5,
    )


def test_valid_session_start_returns_bounded_current_context() -> None:
    result = _invoke(json.dumps({"hook_event_name": "SessionStart", "source": "startup"}))
    assert result.returncode == 0, result.stderr
    response = json.loads(result.stdout)
    context = response["hookSpecificOutput"]["additionalContext"]
    assert response["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "AGENTS.md" in context
    assert "Phase 0" in context
    assert len(context) < 2500


@pytest.mark.parametrize(
    "payload",
    [
        "{not json",
        json.dumps({"hook_event_name": "PreToolUse", "source": "startup"}),
        json.dumps({"hook_event_name": "SessionStart", "source": "unrecognized"}),
        "x" * 9000,
    ],
)
def test_invalid_input_fails_without_echoing_payload(payload: str) -> None:
    result = _invoke(payload)
    assert result.returncode != 0
    assert result.stdout == ""
    assert payload not in result.stderr


def test_missing_status_fails_closed_in_isolated_renderer(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(HOOK))
    render_context = cast(Callable[[Path], str], namespace["render_context"])
    with pytest.raises(FileNotFoundError):
        render_context(tmp_path)


def test_oversized_status_is_rejected(tmp_path: Path) -> None:
    namespace = runpy.run_path(str(HOOK))
    render_context = cast(Callable[[Path], str], namespace["render_context"])
    status_path = tmp_path / "harness" / "status.md"
    status_path.parent.mkdir()
    status_path.write_text("x" * 16385)
    with pytest.raises(ValueError, match="size limit"):
        render_context(tmp_path)
