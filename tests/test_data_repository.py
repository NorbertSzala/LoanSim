"""SQLite history tests with real files and transactions."""

import sqlite3
from dataclasses import replace
from datetime import datetime
from pathlib import Path

import pytest

from loansim.data.codec import encode_snapshot
from loansim.data.repository import ScenarioRepository
from test_data_codec import sample_snapshot


def test_create_reopen_update_duplicate_delete(tmp_path: Path) -> None:
    repo = ScenarioRepository(tmp_path / "history.sqlite3")
    snapshot = sample_snapshot()
    first = repo.save("Apartment", "#3355AA", "note", snapshot)
    assert first.id
    assert first.snapshot == snapshot
    assert datetime.fromisoformat(first.created_at).tzinfo is not None
    assert repo.get(first.id) == first
    assert [item.name for item in repo.list_scenarios()] == ["Apartment"]

    updated = repo.save("Updated", "#3355AA", "new note", snapshot, scenario_id=first.id)
    assert updated.created_at == first.created_at
    assert updated.name == "Updated"
    copy = repo.duplicate(first.id, "Copy")
    assert copy.id != first.id
    assert copy.snapshot == snapshot
    assert {item.name for item in repo.list_scenarios()} == {"Updated", "Copy"}

    repo.delete(first.id)
    assert repo.get(first.id) is None
    assert repo.get(copy.id) == copy


def test_duplicate_preserves_engine_provenance_and_renames_entered_state(tmp_path: Path) -> None:
    db = tmp_path / "history.sqlite3"
    repo = ScenarioRepository(db)
    snapshot = replace(
        sample_snapshot(),
        original_inputs={"fields": {"name": "Original", "price": "1250.00"}, "locks": []},
    )
    original = repo.save("Original", "#3355AA", "note", snapshot)
    with sqlite3.connect(db) as connection:
        connection.execute(
            "UPDATE scenarios SET engine_version=? WHERE id=?", ("0.0.9", original.id)
        )

    copied = repo.duplicate(original.id, "Copy")

    assert copied.engine_version == "0.0.9"
    assert copied.snapshot.result == snapshot.result
    assert copied.snapshot.original_inputs["fields"]["name"] == "Copy"  # type: ignore[index]
    assert repo.get(original.id).snapshot.original_inputs["fields"]["name"] == "Original"  # type: ignore[index,union-attr]


def test_failed_update_does_not_change_previous_snapshot(tmp_path: Path) -> None:
    repo = ScenarioRepository(tmp_path / "history.sqlite3")
    original = repo.save("Before", "#3355AA", "", sample_snapshot())
    with pytest.raises(ValueError):
        repo.save("After", "invalid", "", sample_snapshot(), scenario_id=original.id)
    assert repo.get(original.id) == original


def test_sqlite_abort_during_update_preserves_record(tmp_path: Path) -> None:
    db = tmp_path / "history.sqlite3"
    repo = ScenarioRepository(db)
    original = repo.save("Before", "#3355AA", "", sample_snapshot())
    with sqlite3.connect(db) as connection:
        connection.execute(
            "CREATE TRIGGER fail_update BEFORE UPDATE ON scenarios "
            "BEGIN SELECT RAISE(ABORT, 'forced failure'); END"
        )
    with pytest.raises(sqlite3.IntegrityError, match="forced failure"):
        repo.save("After", "#3355AA", "", sample_snapshot(), scenario_id=original.id)
    assert repo.get(original.id) == original


def test_modified_snapshot_is_rejected_instead_of_displayed(tmp_path: Path) -> None:
    db = tmp_path / "history.sqlite3"
    repo = ScenarioRepository(db)
    saved = repo.save("Apartment", "#3355AA", "", sample_snapshot())
    with sqlite3.connect(db) as connection:
        payload = connection.execute(
            "SELECT snapshot_json FROM scenarios WHERE id=?", (saved.id,)
        ).fetchone()[0]
        assert '"15.02"' in payload
        connection.execute(
            "UPDATE scenarios SET snapshot_json=? WHERE id=?",
            (payload.replace('"15.02"', '"15.03"', 1), saved.id),
        )
    with pytest.raises(ValueError, match="integrity"):
        repo.get(saved.id)


def test_migrate_v1_preserves_existing_record(tmp_path: Path) -> None:
    db = tmp_path / "legacy.sqlite3"
    snapshot = sample_snapshot()
    with sqlite3.connect(db) as connection:
        connection.execute(
            "CREATE TABLE scenarios (id TEXT PRIMARY KEY, name TEXT NOT NULL, color TEXT NOT NULL, "
            "notes TEXT NOT NULL, created_at TEXT NOT NULL, modified_at TEXT NOT NULL, "
            "snapshot_json TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO scenarios VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "old-id",
                "Old",
                "#3355AA",
                "legacy",
                "2026-01-01T12:00:00+00:00",
                "2026-01-01T12:00:00+00:00",
                encode_snapshot(snapshot),
            ),
        )
        connection.execute("PRAGMA user_version = 1")
    repo = ScenarioRepository(db)
    old = repo.get("old-id")
    assert old is not None
    assert old.snapshot == snapshot
    assert old.created_at == "2026-01-01T12:00:00+00:00"
    with sqlite3.connect(db) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2


def test_future_schema_is_rejected_without_mutation(tmp_path: Path) -> None:
    db = tmp_path / "future.sqlite3"
    with sqlite3.connect(db) as connection:
        connection.execute("PRAGMA user_version = 99")
    with pytest.raises(ValueError, match="newer"):
        ScenarioRepository(db)
    with sqlite3.connect(db) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 99


def test_failed_migration_keeps_legacy_schema_and_version(tmp_path: Path) -> None:
    db = tmp_path / "broken-legacy.sqlite3"
    with sqlite3.connect(db) as connection:
        connection.execute("CREATE TABLE scenarios (id TEXT PRIMARY KEY, engine_version TEXT)")
        connection.execute("INSERT INTO scenarios VALUES ('old-id', 'old-version')")
        connection.execute("PRAGMA user_version = 1")
    with pytest.raises(sqlite3.OperationalError):
        ScenarioRepository(db)
    with sqlite3.connect(db) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert (
            connection.execute("SELECT engine_version FROM scenarios").fetchone()[0]
            == "old-version"
        )


def test_new_database_creation_rolls_back_if_migration_is_interrupted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "interrupted.sqlite3"

    def blocked_connect(self: ScenarioRepository) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.set_authorizer(
            lambda action, *_args: (
                sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_ALTER_TABLE else sqlite3.SQLITE_OK
            )
        )
        return connection

    with monkeypatch.context() as patcher:
        patcher.setattr(ScenarioRepository, "_connect", blocked_connect)
        with pytest.raises(sqlite3.DatabaseError):
            ScenarioRepository(db)
    with sqlite3.connect(db) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 0
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='scenarios'"
            ).fetchone()
            is None
        )
