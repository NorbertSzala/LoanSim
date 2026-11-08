"""Transactional SQLite history with explicit schema migrations."""

import hashlib
import re
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

from loansim.data.codec import ScenarioSnapshot, decode_snapshot, encode_snapshot

SCHEMA_VERSION = 2
_COLOR = re.compile(r"#[0-9a-fA-F]{6}\Z")


@dataclass(frozen=True, slots=True)
class ScenarioSummary:
    id: str
    name: str
    color: str
    created_at: str
    modified_at: str


@dataclass(frozen=True, slots=True)
class SavedScenario(ScenarioSummary):
    notes: str
    engine_version: str
    snapshot: ScenarioSnapshot


class ScenarioRepository:
    """One connection per operation permits safe use from a worker thread."""

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._migrate()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _migrate(self) -> None:
        with self._transaction() as connection:
            current = connection.execute("PRAGMA user_version").fetchone()[0]
            if current > SCHEMA_VERSION:
                raise ValueError("database schema is newer than this application")
            if current == 0:
                connection.execute(
                    "CREATE TABLE scenarios (id TEXT PRIMARY KEY, name TEXT NOT NULL, "
                    "color TEXT NOT NULL, notes TEXT NOT NULL, created_at TEXT NOT NULL, "
                    "modified_at TEXT NOT NULL, snapshot_json TEXT NOT NULL)"
                )
                connection.execute("PRAGMA user_version = 1")
                current = 1
            if current == 1:
                connection.execute(
                    "ALTER TABLE scenarios ADD COLUMN engine_version TEXT NOT NULL DEFAULT 'pre-v2'"
                )
                connection.execute(
                    "ALTER TABLE scenarios ADD COLUMN snapshot_sha256 TEXT NOT NULL DEFAULT ''"
                )
                for row in connection.execute("SELECT id, snapshot_json FROM scenarios").fetchall():
                    connection.execute(
                        "UPDATE scenarios SET snapshot_sha256=? WHERE id=?",
                        (self._digest(row["snapshot_json"]), row["id"]),
                    )
                connection.execute("PRAGMA user_version = 2")

    @staticmethod
    def _digest(payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _validate(name: str, color: str, notes: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("scenario name is required")
        if not isinstance(color, str) or _COLOR.fullmatch(color) is None:
            raise ValueError("scenario color must be #RRGGBB")
        if not isinstance(notes, str):
            raise ValueError("scenario notes must be text")

    def save(
        self,
        name: str,
        color: str,
        notes: str,
        snapshot: ScenarioSnapshot,
        *,
        scenario_id: str | None = None,
        engine_version: str | None = None,
    ) -> SavedScenario:
        """Insert or update atomically, preserving creation time on edits."""
        self._validate(name, color, notes)
        payload = encode_snapshot(snapshot)
        digest = self._digest(payload)
        now = datetime.now(UTC).isoformat()
        engine_version = engine_version if engine_version is not None else version("loansim")
        if not isinstance(engine_version, str) or not engine_version.strip():
            raise ValueError("engine version is required")
        identifier = scenario_id or str(uuid4())
        with self._transaction() as connection:
            if scenario_id is None:
                connection.execute(
                    "INSERT INTO scenarios (id, name, color, notes, created_at, modified_at, "
                    "snapshot_json, engine_version, snapshot_sha256) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        identifier,
                        name.strip(),
                        color,
                        notes,
                        now,
                        now,
                        payload,
                        engine_version,
                        digest,
                    ),
                )
            else:
                cursor = connection.execute(
                    "UPDATE scenarios SET name=?, color=?, notes=?, modified_at=?, "
                    "snapshot_json=?, engine_version=?, snapshot_sha256=? WHERE id=?",
                    (name.strip(), color, notes, now, payload, engine_version, digest, identifier),
                )
                if cursor.rowcount != 1:
                    raise KeyError("scenario does not exist")
        saved = self.get(identifier)
        if saved is None:
            raise RuntimeError("saved scenario disappeared")
        return saved

    def get(self, scenario_id: str) -> SavedScenario | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM scenarios WHERE id=?", (scenario_id,)
            ).fetchone()
        if row is None:
            return None
        if self._digest(row["snapshot_json"]) != row["snapshot_sha256"]:
            raise ValueError("scenario snapshot integrity check failed")
        return SavedScenario(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            created_at=row["created_at"],
            modified_at=row["modified_at"],
            notes=row["notes"],
            engine_version=row["engine_version"],
            snapshot=decode_snapshot(row["snapshot_json"]),
        )

    def list_scenarios(self) -> tuple[ScenarioSummary, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT id, name, color, created_at, modified_at FROM scenarios "
                "ORDER BY modified_at DESC, id"
            ).fetchall()
        return tuple(ScenarioSummary(**dict(row)) for row in rows)

    def duplicate(self, scenario_id: str, new_name: str) -> SavedScenario:
        existing = self.get(scenario_id)
        if existing is None:
            raise KeyError("scenario does not exist")
        self._validate(new_name, existing.color, existing.notes)
        original_inputs = dict(existing.snapshot.original_inputs)
        fields_state = original_inputs.get("fields")
        if isinstance(fields_state, dict):
            renamed_fields = dict(fields_state)
            renamed_fields["name"] = new_name.strip()
            original_inputs["fields"] = renamed_fields
        copied_snapshot = replace(existing.snapshot, original_inputs=original_inputs)
        return self.save(
            new_name,
            existing.color,
            existing.notes,
            copied_snapshot,
            engine_version=existing.engine_version,
        )

    def delete(self, scenario_id: str) -> None:
        with self._transaction() as connection:
            cursor = connection.execute("DELETE FROM scenarios WHERE id=?", (scenario_id,))
            if cursor.rowcount != 1:
                raise KeyError("scenario does not exist")
