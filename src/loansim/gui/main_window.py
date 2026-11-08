"""Offline single-scenario workflow connecting Qt, core, and history."""

import os
from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from typing import Any

from PySide6.QtCore import QCoreApplication, QStandardPaths, QThreadPool, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox, QScrollArea, QTabWidget

from loansim.core.amortization import simulate
from loansim.data.codec import ScenarioSnapshot
from loansim.data.repository import SavedScenario, ScenarioRepository
from loansim.gui.history_view import HistoryView
from loansim.gui.results_view import ResultsView
from loansim.gui.scenario_form import ScenarioForm
from loansim.gui.strings import localize_core_error, tr
from loansim.gui.worker import Task


def _default_db_path() -> Path:
    QCoreApplication.setApplicationName(tr("app_name"))
    configured = os.environ.get("LOANSIM_DATA_DIR")
    directory = (
        Path(configured)
        if configured
        else Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    )
    return directory / "history.sqlite3"


class LoanSimWindow(QMainWindow):
    def __init__(self, db_path: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle(tr("app_name"))
        self.resize(1100, 800)
        self.db_path = db_path or _default_db_path()
        self.pool = QThreadPool.globalInstance()
        self._tasks: list[Task] = []
        self._generation = 0
        self._open_sequence = 0
        self._loading = False
        self._dirty = False
        self._saving = False
        self._close_when_idle = False
        self._preview_snapshot: ScenarioSnapshot | None = None
        self.current_id: str | None = None
        self.current_snapshot: ScenarioSnapshot | None = None
        self._snapshot_engine_version: str | None = None
        self._validation_timer = QTimer(self)
        self._validation_timer.setSingleShot(True)
        self._validation_timer.setInterval(75)
        self._validation_timer.timeout.connect(self._validate_current)

        self.tabs = QTabWidget()
        self.form = ScenarioForm()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.form)
        self.tabs.addTab(scroll, tr("tab_simulation"))
        self.result_view = ResultsView()
        self.tabs.addTab(self.result_view, tr("tab_results"))
        self.history = HistoryView()
        self.tabs.addTab(self.history, tr("tab_history"))
        self.setCentralWidget(self.tabs)
        self.form.changed.connect(self._form_changed)
        self.form.calculate_button.clicked.connect(self._calculate)
        self.result_view.save_button.clicked.connect(self._save)
        self.history.open_requested.connect(self._open)
        self.history.duplicate_requested.connect(self._duplicate)
        self.history.delete_requested.connect(self._delete)
        self._refresh_history()

    def _repository(self) -> ScenarioRepository:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return ScenarioRepository(self.db_path)

    def _run(
        self,
        operation: Callable[[], object],
        on_success: Callable[[Any], None],
        on_failure: Callable[[str], None] | None = None,
    ) -> None:
        task = Task(operation)
        self._tasks.append(task)

        def done(value: object) -> None:
            self._tasks.remove(task)
            on_success(value)
            self._close_if_idle()

        def failed(message: str) -> None:
            self._tasks.remove(task)
            if on_failure is None:
                self.statusBar().showMessage(message)
                self.form.error_label.setText(message)
            else:
                on_failure(message)
            self._close_if_idle()

        task.signals.finished.connect(done)
        task.signals.failed.connect(failed)
        self.pool.start(task)

    def _close_if_idle(self) -> None:
        if self._close_when_idle and not self._tasks:
            self._close_when_idle = False
            QTimer.singleShot(0, self.close)

    def _form_changed(self) -> None:
        if self._loading:
            return
        self._generation += 1
        self._dirty = True
        self._validation_timer.stop()
        original = self.form.export_state()
        snapshot = self.current_snapshot or self._preview_snapshot
        if snapshot is not None and self._same_financial_state(original, snapshot.original_inputs):
            updated = replace(
                snapshot,
                original_inputs=original,
            )
            valid = not self.form.error_text
            if valid and self.current_snapshot is not None:
                self._loading = True
                try:
                    self.form.restore_derived_state(snapshot.derived_inputs)
                finally:
                    self._loading = False
            if self.current_snapshot is not None:
                self.current_snapshot = updated
            else:
                self._preview_snapshot = updated
            self.result_view.save_button.setEnabled(
                valid and self.current_snapshot is not None and not self._saving
            )
            self.form.calculate_button.setEnabled(valid)
            if valid:
                self.result_view.chart.set_color(self.form.color.text())
            return
        self._preview_snapshot = None
        self.current_snapshot = None
        self._snapshot_engine_version = None
        self.result_view.invalidate()
        self.form.calculate_button.setEnabled(False)
        if not self.form.error_text:
            self._validation_timer.start()

    @staticmethod
    def _same_financial_state(current: dict[str, object], saved: dict[str, object]) -> bool:
        current_fields = current.get("fields")
        saved_fields = saved.get("fields")
        if not isinstance(current_fields, dict) or not isinstance(saved_fields, dict):
            return False
        current_inputs = {
            key: value for key, value in current.items() if key not in ("fields", "notes")
        }
        saved_inputs = {
            key: value for key, value in saved.items() if key not in ("fields", "notes")
        }
        current_money = {
            key: value for key, value in current_fields.items() if key not in ("name", "color")
        }
        saved_money = {
            key: value for key, value in saved_fields.items() if key not in ("name", "color")
        }
        return current_inputs == saved_inputs and current_money == saved_money

    @staticmethod
    def _validation_message(message: str) -> tuple[str, str | None]:
        translated, field = localize_core_error(message)
        return (
            (translated, field)
            if translated != message
            else (tr("cannot_calculate", detail=message), None)
        )

    def _validate_current(self) -> None:
        if self.form.error_text:
            return
        try:
            terms, rate, plan, charges = self.form.build_inputs()
            original = self.form.export_state()
            derived = self.form.derived_state()
        except ValueError as error:
            self.form.set_external_error(str(error))
            return
        generation = self._generation

        def calculation() -> ScenarioSnapshot:
            return ScenarioSnapshot(
                original,
                derived,
                terms,
                rate,
                plan,
                charges,
                simulate(terms, rate, plan, charges=charges),
            )

        def ready(snapshot: ScenarioSnapshot) -> None:
            if generation == self._generation:
                self._preview_snapshot = snapshot
                self.form.calculate_button.setEnabled(True)

        def failed(message: str) -> None:
            if generation == self._generation:
                user_message, field = self._validation_message(message)
                self.form.set_external_error(user_message, field)

        self._run(calculation, ready, failed)

    def _calculate(self) -> None:
        if self._preview_snapshot is not None:
            self.current_snapshot = self._preview_snapshot
            self._snapshot_engine_version = None
            self.result_view.set_result(
                self._preview_snapshot.result, scenario_color=self.form.color.text()
            )
            self.tabs.setCurrentWidget(self.result_view)
            self.statusBar().showMessage(tr("calculation_ready"))
            return
        try:
            terms, rate, plan, charges = self.form.build_inputs()
            original = self.form.export_state()
            derived = self.form.derived_state()
        except ValueError as error:
            self.form.error_label.setText(str(error))
            return
        generation = self._generation
        self.form.calculate_button.setEnabled(False)

        def calculation() -> ScenarioSnapshot:
            return ScenarioSnapshot(
                original,
                derived,
                terms,
                rate,
                plan,
                charges,
                simulate(terms, rate, plan, charges=charges),
            )

        def ready(snapshot: ScenarioSnapshot) -> None:
            if generation == self._generation:
                self.current_snapshot = snapshot
                self._snapshot_engine_version = None
                self.result_view.set_result(snapshot.result, scenario_color=self.form.color.text())
                self.tabs.setCurrentWidget(self.result_view)
                self.statusBar().showMessage(tr("calculation_ready"))
            self.form.calculate_button.setEnabled(not self.form.error_text)

        def failed(message: str) -> None:
            if generation == self._generation:
                user_message, field = self._validation_message(message)
                self.form.set_external_error(user_message, field)

        self._run(calculation, ready, failed)

    def _save(self) -> None:
        snapshot = self.current_snapshot
        if snapshot is None or self._saving:
            return
        self._saving = True
        self.result_view.save_button.setEnabled(False)
        name = self.form.name.text()
        color = self.form.color.text()
        notes = self.form.notes.toPlainText()
        scenario_id = self.current_id
        engine_version = self._snapshot_engine_version
        generation = self._generation

        def save() -> SavedScenario:
            return self._repository().save(
                name,
                color,
                notes,
                snapshot,
                scenario_id=scenario_id,
                engine_version=engine_version,
            )

        def saved(record: SavedScenario) -> None:
            self._saving = False
            if (
                generation == self._generation
                and self.current_id == scenario_id
                and self.current_snapshot is snapshot
            ):
                self.current_id = record.id
                self._dirty = False
                self.result_view.save_button.setEnabled(True)
            self.statusBar().showMessage(tr("scenario_saved"))
            self._refresh_history()

        def failed(message: str) -> None:
            self._saving = False
            if generation == self._generation and self.current_snapshot is snapshot:
                self.result_view.save_button.setEnabled(True)
            self.statusBar().showMessage(message)
            self.form.error_label.setText(message)

        self._run(save, saved, failed)

    def _refresh_history(self) -> None:
        self._run(lambda: self._repository().list_scenarios(), self.history.set_scenarios)

    def _open(self, scenario_id: str) -> None:
        if (
            self._dirty
            and QMessageBox.question(self, tr("unsaved_title"), tr("open_discard_question"))
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._open_sequence += 1
        open_sequence = self._open_sequence
        generation = self._generation

        def opened(record: SavedScenario | None) -> None:
            if open_sequence != self._open_sequence:
                return
            if generation != self._generation:
                self.statusBar().showMessage(tr("open_cancelled"))
                return
            if record is None:
                self.statusBar().showMessage(tr("scenario_missing"))
                return
            self._loading = True
            try:
                self.form.load_state(
                    record.snapshot.original_inputs, record.snapshot.derived_inputs
                )
                self.form.name.setText(record.name)
                self.form.color.setText(record.color)
                self.form.notes.setPlainText(record.notes)
            except ValueError as error:
                self.statusBar().showMessage(tr("open_failed", detail=error))
                return
            finally:
                self._loading = False
            self._generation += 1
            self._validation_timer.stop()
            self._preview_snapshot = None
            self.current_id = record.id
            self.current_snapshot = record.snapshot
            self._snapshot_engine_version = record.engine_version
            self._dirty = False
            self.result_view.set_result(
                record.snapshot.result,
                engine_version=record.engine_version,
                scenario_color=record.color,
            )
            self.tabs.setCurrentWidget(self.result_view)
            self.statusBar().showMessage(tr("scenario_opened"))

        def failed(message: str) -> None:
            if open_sequence == self._open_sequence and generation == self._generation:
                self.statusBar().showMessage(tr("open_failed", detail=message))

        self._run(lambda: self._repository().get(scenario_id), opened, failed)

    def _duplicate(self, scenario_id: str) -> None:
        def duplicate() -> SavedScenario:
            repo = self._repository()
            original = repo.get(scenario_id)
            if original is None:
                raise KeyError(tr("scenario_missing"))
            return repo.duplicate(scenario_id, tr("copy_suffix", name=original.name))

        self._run(duplicate, lambda _record: self._refresh_history())

    def _delete(self, scenario_id: str) -> None:
        if (
            QMessageBox.question(self, tr("delete_title"), tr("delete_question"))
            != QMessageBox.StandardButton.Yes
        ):
            return

        def deleted(_value: object) -> None:
            if self.current_id == scenario_id:
                self.current_id = None
            self.statusBar().showMessage(tr("scenario_deleted"))
            self._refresh_history()

        self._run(lambda: self._repository().delete(scenario_id), deleted)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._tasks:
            self.statusBar().showMessage(tr("wait_operation"))
            self._close_when_idle = True
            event.ignore()
            return
        if (
            self._dirty
            and QMessageBox.question(
                self,
                tr("unsaved_title"),
                tr("close_discard_question"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            event.ignore()
            return
        event.accept()


def create_window(db_path: Path | None = None) -> LoanSimWindow:
    """Create the Phase 2 offline window with an optional isolated database."""
    return LoanSimWindow(db_path)
