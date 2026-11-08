"""Offscreen application workflow using real core and SQLite storage."""

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path
from threading import Event
from time import sleep

import pytest
from PySide6.QtCore import QCoreApplication, Qt, QTimer
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QLineEdit, QMessageBox

from loansim.core.amortization import SimulationResult
from loansim.core.amortization import simulate as real_simulate
from loansim.core.models import Charge, LoanTerms, OverpaymentPlan
from loansim.core.rates import RatePlan
from loansim.data.codec import ScenarioSnapshot
from loansim.data.repository import SavedScenario, ScenarioRepository
from loansim.gui import main_window
from loansim.gui.main_window import create_window


def _until(app: QCoreApplication, condition: Callable[[], bool], timeout_ms: int = 5000) -> None:
    for _ in range(timeout_ms // 10):
        app.processEvents()
        if condition():
            return
        QTest.qWait(10)
    raise AssertionError("asynchronous operation did not finish")


def _prepared_snapshot(
    app: QCoreApplication, window: main_window.LoanSimWindow
) -> ScenarioSnapshot:
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "2"),
        ("nominal_annual", "0.12"),
    ):
        window.form.fields[key].setText(value)
    _until(app, lambda: window.form.calculate_button.isEnabled() and not window._tasks)
    terms, rate, plan, charges = window.form.build_inputs()
    return ScenarioSnapshot(
        window.form.export_state(),
        window.form.derived_state(),
        terms,
        rate,
        plan,
        charges,
        real_simulate(terms, rate, plan, charges=charges),
    )


def test_calculate_save_reopen_duplicate_and_delete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    window.show()
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "2"),
        ("nominal_annual", "0.12"),
        ("start_date", "2026-01-31"),
    ):
        field = window.findChild(QLineEdit, key)
        assert field is not None
        field.setText(value)
    window.form.color.setText("#12AB34")
    window.form.color.setText("#12AB34")
    window.form.color.setText("#12AB34")
    _until(app, lambda: window.form.calculate_button.isEnabled())
    QTest.mouseClick(window.form.calculate_button, Qt.MouseButton.LeftButton)
    _until(app, lambda: window.result_view.save_button.isEnabled())
    assert window.result_view.total_interest.text() == "15.02 PLN"
    assert window.result_view.chart.canvas.color.name() == "#12ab34"
    assert window.result_view.chart.canvas.color.name() == "#12ab34"
    assert window.result_view.chart.canvas.color.name() == "#12ab34"
    QTest.mouseClick(window.result_view.save_button, Qt.MouseButton.LeftButton)
    _until(
        app,
        lambda: (
            len(ScenarioRepository(db).list_scenarios()) == 1
            and window.history.scenarios.count() == 1
        ),
    )
    assert window.history.scenarios.count() == 1
    assert not window._dirty

    window.form.notes.setPlainText("unsaved note")
    assert window._dirty
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.No)
    window.history.scenarios.setCurrentRow(0)
    QTest.mouseClick(window.history.open_button, Qt.MouseButton.LeftButton)
    QTest.qWait(50)
    assert window.form.notes.toPlainText() == "unsaved note"
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    QTest.mouseClick(window.history.open_button, Qt.MouseButton.LeftButton)
    _until(app, lambda: window.form.notes.toPlainText() == "")

    window.form.fields["price"].setText("1300.00")
    assert not window.result_view.save_button.isEnabled()
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    window.history.scenarios.setCurrentRow(0)
    QTest.mouseClick(window.history.open_button, Qt.MouseButton.LeftButton)
    _until(app, lambda: window.form.fields["price"].text() == "1200.00")
    assert window.result_view.total_interest.text() == "15.02 PLN"
    assert window.result_view.chart.canvas.color.name() == "#12ab34"
    assert window.result_view.chart.canvas.color.name() == "#12ab34"
    assert window.result_view.chart.canvas.color.name() == "#12ab34"

    QTest.mouseClick(window.history.duplicate_button, Qt.MouseButton.LeftButton)
    _until(app, lambda: len(ScenarioRepository(db).list_scenarios()) == 2)
    window.history.scenarios.setCurrentRow(0)
    QTest.mouseClick(window.history.delete_button, Qt.MouseButton.LeftButton)
    _until(app, lambda: len(ScenarioRepository(db).list_scenarios()) == 1)
    window.form.notes.setPlainText("draft to keep")
    _until(app, lambda: not window._tasks)
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.No)
    window.close()
    assert window.isVisible()
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    window.close()
    assert not window.isVisible()


def test_slow_calculation_keeps_event_loop_responsive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    window = create_window(db_path=tmp_path / "history.sqlite3")
    window.show()
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "2"),
        ("nominal_annual", "0.12"),
    ):
        window.form.fields[key].setText(value)

    def delayed_simulate(
        terms: LoanTerms,
        rate_plan: RatePlan,
        overpayments: OverpaymentPlan | None = None,
        *,
        charges: tuple[Charge, ...] = (),
    ) -> SimulationResult:
        sleep(0.2)
        return real_simulate(terms, rate_plan, overpayments, charges=charges)

    monkeypatch.setattr(main_window, "simulate", delayed_simulate)
    timer_saw_pending: list[bool] = []
    QTimer.singleShot(
        30, lambda: timer_saw_pending.append(not window.form.calculate_button.isEnabled())
    )
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    _until(app, lambda: bool(timer_saw_pending))
    assert timer_saw_pending == [True]
    _until(app, lambda: window.form.calculate_button.isEnabled())
    QTest.mouseClick(window.form.calculate_button, Qt.MouseButton.LeftButton)
    _until(app, lambda: window.result_view.save_button.isEnabled())
    window.close()


def test_invalid_payment_cap_is_rejected_before_calculation(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = create_window(db_path=tmp_path / "history.sqlite3")
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "2"),
        ("nominal_annual", "0.12"),
        ("monthly_cap", "1.00"),
    ):
        window.form.fields[key].setText(value)

    _until(app, lambda: "limit" in window.form.error_text.lower())
    assert not window.form.calculate_button.isEnabled()
    assert "red" in window.form.fields["monthly_cap"].styleSheet()

    window.form.fields["monthly_cap"].setText("1000.00")
    _until(app, lambda: window.form.calculate_button.isEnabled())
    window._dirty = False
    window.close()


def test_double_save_creates_one_record_and_reopen_uses_stored_derivation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "2"),
        ("nominal_annual", "0.12"),
    ):
        window.form.fields[key].setText(value)
    _until(app, lambda: window.form.calculate_button.isEnabled())
    window._calculate()
    _until(app, lambda: window.current_snapshot is not None)
    snapshot = window.current_snapshot
    assert snapshot is not None
    stored_derived = dict(snapshot.derived_inputs)
    saved_loan = stored_derived["purchase_loan"]
    assert isinstance(saved_loan, dict)
    stored_derived["purchase_loan"] = {**saved_loan, "value": "999.00"}
    window.current_snapshot = replace(snapshot, derived_inputs=stored_derived)

    window._save()
    window._save()
    _until(app, lambda: len(ScenarioRepository(db).list_scenarios()) == 1 and not window._tasks)
    assert len(ScenarioRepository(db).list_scenarios()) == 1

    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    scenario_id = ScenarioRepository(db).list_scenarios()[0].id
    window._open(scenario_id)
    _until(app, lambda: window.current_id == scenario_id and not window._tasks)
    assert window.form.fields["purchase_loan"].text() == "999.00"
    window._dirty = False
    window.close()


def test_late_save_cannot_replace_the_opened_scenario(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "2"),
        ("nominal_annual", "0.12"),
    ):
        window.form.fields[key].setText(value)
    _until(app, lambda: window.form.calculate_button.isEnabled())
    window._calculate()
    _until(app, lambda: window.current_snapshot is not None)
    snapshot = window.current_snapshot
    assert snapshot is not None
    other = ScenarioRepository(db).save("Other", "#3355AA", "", snapshot)
    entered_save = Event()
    release_save = Event()
    real_save = ScenarioRepository.save

    def delayed_save(
        repository: ScenarioRepository,
        name: str,
        color: str,
        notes: str,
        saved_snapshot: ScenarioSnapshot,
        *,
        scenario_id: str | None = None,
        engine_version: str | None = None,
    ) -> SavedScenario:
        if name == window.form.name.text():
            entered_save.set()
            assert release_save.wait(5)
        return real_save(
            repository,
            name,
            color,
            notes,
            saved_snapshot,
            scenario_id=scenario_id,
            engine_version=engine_version,
        )

    monkeypatch.setattr(ScenarioRepository, "save", delayed_save)
    window._save()
    _until(app, entered_save.is_set)
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)
    window._open(other.id)
    _until(app, lambda: window.current_id == other.id)
    release_save.set()
    _until(app, lambda: not window._tasks)
    assert window.current_id == other.id
    assert len(ScenarioRepository(db).list_scenarios()) == 2
    window._dirty = False
    window.close()


def test_resaving_reopened_result_preserves_its_engine_version(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    snapshot = _prepared_snapshot(app, window)
    original = ScenarioRepository(db).save(
        "Older result", "#3355AA", "", snapshot, engine_version="0.0.9"
    )
    window._dirty = False

    window._open(original.id)
    _until(app, lambda: window.current_id == original.id and not window._tasks)
    window._save()
    _until(app, lambda: not window._saving and not window._tasks)

    saved = ScenarioRepository(db).get(original.id)
    assert saved is not None
    assert saved.engine_version == "0.0.9"
    assert saved.snapshot.result == snapshot.result
    window.close()


def test_latest_open_request_wins_when_earlier_request_finishes_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    snapshot = _prepared_snapshot(app, window)
    repository = ScenarioRepository(db)
    first = repository.save("First", "#3355AA", "", snapshot)
    second = repository.save("Second", "#3355AA", "", snapshot)
    original_get = ScenarioRepository.get
    second_started = Event()
    release_second = Event()

    def delayed_get(repo: ScenarioRepository, scenario_id: str) -> SavedScenario | None:
        if scenario_id == second.id:
            second_started.set()
            assert release_second.wait(5)
        return original_get(repo, scenario_id)

    monkeypatch.setattr(ScenarioRepository, "get", delayed_get)
    window._dirty = False
    window._open(first.id)
    window._open(second.id)
    _until(app, second_started.is_set)
    _until(app, lambda: len(window._tasks) == 1)
    release_second.set()
    _until(app, lambda: not window._tasks)

    assert window.current_id == second.id
    assert window.form.name.text() == "Second"
    window.close()


def test_unrestorable_snapshot_does_not_replace_current_form(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    snapshot = _prepared_snapshot(app, window)
    repository = ScenarioRepository(db)
    valid = repository.save("Valid", "#3355AA", "", snapshot)
    broken = repository.save("Broken", "#3355AA", "", replace(snapshot, original_inputs={}))
    window._dirty = False
    window._open(valid.id)
    _until(app, lambda: window.current_id == valid.id and not window._tasks)
    original_state = window.form.export_state()

    window._open(broken.id)
    _until(app, lambda: not window._tasks)

    assert window.current_id == valid.id
    assert window.form.export_state() == original_state
    assert "Nie można otworzyć" in window.statusBar().currentMessage()
    assert repository.get(broken.id) is not None
    window.close()


def test_unrestorable_snapshot_keeps_existing_validation_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    snapshot = _prepared_snapshot(app, window)
    repository = ScenarioRepository(db)
    valid = repository.save("Valid", "#3355AA", "", snapshot)
    broken = repository.save("Broken", "#3355AA", "", replace(snapshot, original_inputs={}))
    window._dirty = False
    window._open(valid.id)
    _until(app, lambda: window.current_id == valid.id and not window._tasks)
    window.form.fields["price"].setText("bad")
    original_error = window.form.error_text
    assert original_error
    assert not window.form.calculate_button.isEnabled()
    monkeypatch.setattr(QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes)

    window._open(broken.id)
    _until(app, lambda: not window._tasks)

    assert window.current_id == valid.id
    assert window.form.fields["price"].text() == "bad"
    assert window.form.error_text == original_error
    assert window.form.error_label.text() == original_error
    assert not window.form.calculate_button.isEnabled()
    window._dirty = False
    window.close()


def test_reopened_entered_field_is_editable_after_derived_view(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    snapshot = _prepared_snapshot(app, window)
    saved = ScenarioRepository(db).save("Entered price", "#3355AA", "", snapshot)
    window.form.locks["purchase_loan"].setChecked(True)
    window.form.locks["price"].setChecked(False)
    price = window.form.fields["price"]
    assert price.text() == "1200.00"
    assert price.isReadOnly()
    window._dirty = False

    window._open(saved.id)
    _until(app, lambda: window.current_id == saved.id and not window._tasks)

    assert window.form.locks["price"].isChecked()
    assert price.text() == "1200.00"
    assert not price.isReadOnly()
    window.close()


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("name", "Renamed"),
        ("color", "#112233"),
        ("notes", "Updated note"),
    ),
)
def test_metadata_edit_preserves_old_result_and_snapshot_provenance(
    tmp_path: Path, field: str, value: str
) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    window.form.name.setText("Original")
    snapshot = _prepared_snapshot(app, window)
    historical_derived = dict(snapshot.derived_inputs)
    saved_loan = historical_derived["purchase_loan"]
    assert isinstance(saved_loan, dict)
    historical_derived["purchase_loan"] = {
        **saved_loan,
        "value": "999.00",
        "formula": "old engine formula",
    }
    snapshot = replace(snapshot, derived_inputs=historical_derived)
    original = ScenarioRepository(db).save(
        "Original", "#3355AA", "", snapshot, engine_version="0.0.9"
    )
    window._dirty = False
    window._open(original.id)
    _until(app, lambda: window.current_id == original.id and not window._tasks)

    if field == "notes":
        window.form.notes.setPlainText(value)
    else:
        window.form.fields[field].setText(value)
    assert window.result_view.save_button.isEnabled()
    assert window.form.fields["purchase_loan"].text() == "999.00"
    window._save()
    _until(app, lambda: not window._saving and not window._tasks)

    saved = ScenarioRepository(db).get(original.id)
    assert saved is not None
    assert saved.engine_version == "0.0.9"
    assert saved.snapshot.result == snapshot.result
    assert saved.snapshot.derived_inputs == snapshot.derived_inputs
    if field == "notes":
        assert saved.snapshot.original_inputs["notes"] == value
    else:
        fields = saved.snapshot.original_inputs["fields"]
        assert isinstance(fields, dict)
        assert fields[field] == value
    assert getattr(saved, field) == value
    window.close()


def test_obsolete_open_failure_does_not_mark_newer_scenario_invalid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    app = QApplication.instance() or QApplication([])
    db = tmp_path / "history.sqlite3"
    window = create_window(db_path=db)
    snapshot = _prepared_snapshot(app, window)
    repository = ScenarioRepository(db)
    first = repository.save("First", "#3355AA", "", snapshot)
    second = repository.save("Second", "#3355AA", "", snapshot)
    original_get = ScenarioRepository.get
    first_started = Event()
    release_first = Event()

    def delayed_failure(repo: ScenarioRepository, scenario_id: str) -> SavedScenario | None:
        if scenario_id == first.id:
            first_started.set()
            assert release_first.wait(5)
            raise ValueError("obsolete failure")
        return original_get(repo, scenario_id)

    monkeypatch.setattr(ScenarioRepository, "get", delayed_failure)
    window._dirty = False
    window._open(first.id)
    _until(app, first_started.is_set)
    window._open(second.id)
    _until(app, lambda: window.current_id == second.id)
    release_first.set()
    _until(app, lambda: not window._tasks)

    assert window.current_id == second.id
    assert window.form.error_label.text() == ""
    assert "obsolete failure" not in window.statusBar().currentMessage()
    window.close()


def test_color_with_surrounding_spaces_is_rejected_before_chart_update(tmp_path: Path) -> None:
    app = QApplication.instance() or QApplication([])
    window = create_window(db_path=tmp_path / "history.sqlite3")
    _prepared_snapshot(app, window)
    window._calculate()
    _until(app, lambda: window.current_snapshot is not None)

    window.form.color.setText(" #112233 ")

    assert not window.result_view.save_button.isEnabled()
    assert window.form.error_field == "color"
    assert not window.form.calculate_button.isEnabled()
    window._dirty = False
    window.close()
