"""Real offscreen input interactions for entered and derived values."""

from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QLabel, QLineEdit

from loansim.core.rates import PeriodicallyFixedRate, VariableRate
from loansim.gui.main_window import create_window
from loansim.gui.scenario_form import ScenarioForm


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])  # type: ignore[return-value]


def _until(app: QApplication, condition: Callable[[], bool]) -> None:
    for _ in range(500):
        app.processEvents()
        if condition():
            return
        QTest.qWait(10)
    raise AssertionError("asynchronous validation did not finish")


def test_property_derivation_and_lock_preserve_user_values() -> None:
    _app()
    form = ScenarioForm()
    assert form.origin_labels["term_months"].text() == "Wprowadzone"
    price = form.findChild(QLineEdit, "price")
    down = form.findChild(QLineEdit, "down_payment")
    loan = form.findChild(QLineEdit, "purchase_loan")
    assert price is not None and down is not None and loan is not None
    price.setText("300000.00")
    down.setText("60000.00")
    assert loan.text() == "240000.00"
    assert loan.isReadOnly()
    assert "cena - wkład własny" in loan.toolTip()
    origin = form.findChild(QLabel, "origin_purchase_loan")
    assert origin is not None
    assert origin.text() == "Wyliczone"

    lock = form.findChild(QCheckBox, "lock_purchase_loan")
    assert lock is not None
    lock.setChecked(True)
    assert not loan.isReadOnly()
    assert origin.text() == "Wprowadzone"
    price.setText("310000.00")
    assert loan.text() == "240000.00"
    assert form.error_text
    assert not form.calculate_button.isEnabled()


def test_fixed_form_builds_core_inputs_and_rejects_missing_term() -> None:
    _app()
    form = ScenarioForm()
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "2"),
        ("nominal_annual", "0.12"),
        ("start_date", "2026-01-31"),
    ):
        field = form.findChild(QLineEdit, key)
        assert field is not None
        field.setText(value)
    terms, rates, plan, charges = form.build_inputs()
    assert terms.purchase_loan == Decimal("1000.00")
    assert terms.term_months == 2
    assert rates.nominal_annual == Decimal("0.12")  # type: ignore[union-attr]
    assert plan.regular_amount == Decimal("0.00")
    assert charges == ()

    term = form.findChild(QLineEdit, "term_months")
    assert term is not None
    term.clear()
    assert not form.calculate_button.isEnabled()


def test_financed_origination_charge_changes_derived_ltv() -> None:
    _app()
    form = ScenarioForm()
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("nominal_annual", "0.12"),
    ):
        field = form.findChild(QLineEdit, key)
        assert field is not None
        field.setText(value)
    form.add_charge_row()
    funding = form.charges.cellWidget(0, 4)
    assert isinstance(funding, QComboBox)
    assert funding.currentText() == "Środki własne"
    funding.setCurrentIndex(funding.findData("financed"))
    ltv = form.findChild(QLineEdit, "ltv")
    assert ltv is not None
    assert abs(Decimal(ltv.text()) - Decimal("0.91666666666666666667")) < Decimal("1e-20")
    form.charges.selectRow(0)
    form.remove_charge_row()
    assert abs(Decimal(ltv.text()) - Decimal("0.83333333333333333333")) < Decimal("1e-20")


def test_unique_fixed_annuity_payment_derives_term() -> None:
    _app()
    form = ScenarioForm()
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("nominal_annual", "0.12"),
        ("mandatory_installment", "507.51"),
    ):
        field = form.findChild(QLineEdit, key)
        assert field is not None
        field.setText(value)
    term = form.findChild(QLineEdit, "term_months")
    assert term is not None
    term.clear()
    assert term.text() == "2"
    assert term.isReadOnly()
    assert form.build_inputs()[0].term_months == 2


def test_variable_rate_path_gap_disables_calculation(tmp_path: Path) -> None:
    app = _app()
    window = create_window(tmp_path / "history.sqlite3")
    form = window.form
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "3"),
        ("index_annual", "0.05"),
        ("margin", "0.02"),
        ("start_date", "2026-01-01"),
        ("as_of_date", "2025-12-31"),
    ):
        field = form.findChild(QLineEdit, key)
        assert field is not None
        field.setText(value)
    rate_type = form.findChild(QComboBox, "rate_type")
    assert rate_type is not None
    rate_type.setCurrentIndex(rate_type.findData("variable"))
    form.add_rate_row()
    period_item = form.rate_path.item(0, 0)
    index_item = form.rate_path.item(0, 1)
    assert period_item is not None and index_item is not None
    period_item.setText("3")
    index_item.setText("0.06")
    _until(app, lambda: "brak" in form.error_text.lower())
    assert not form.calculate_button.isEnabled()
    assert "brak" in form.error_text.lower()

    period_item.setText("2")
    _until(app, lambda: form.calculate_button.isEnabled())
    assert form.calculate_button.isEnabled(), form.error_text
    terms, rate, _, _ = form.build_inputs()
    assert terms.term_months == 3
    assert isinstance(rate, VariableRate)
    assert rate.observations[1].index_annual == Decimal("0.06")
    window._dirty = False
    _until(app, lambda: not window._tasks)
    window.close()


def test_invalid_price_is_identified_at_field() -> None:
    _app()
    form = ScenarioForm()
    price = form.findChild(QLineEdit, "price")
    assert price is not None
    price.setText("abc")
    assert not form.calculate_button.isEnabled()
    assert "price" in form.error_text
    assert "red" in price.styleSheet()
    assert price.accessibleDescription()


def test_core_validation_message_is_polish_and_attached_to_field() -> None:
    _app()
    form = ScenarioForm()
    price = form.fields["price"]
    price.setText("-1.00")
    assert "dodatnia wartość pola: cena" in form.error_text
    assert "red" in price.styleSheet()
    assert price.accessibleDescription() == form.error_text


def test_invalid_name_and_color_block_calculation() -> None:
    _app()
    form = ScenarioForm()
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("nominal_annual", "0.12"),
    ):
        field = form.findChild(QLineEdit, key)
        assert field is not None
        field.setText(value)
    form.name.clear()
    assert not form.calculate_button.isEnabled()
    form.name.setText("Home")
    form.color.setText("bad")
    assert not form.calculate_button.isEnabled()


def test_form_supports_keyboard_navigation() -> None:
    app = _app()
    form = ScenarioForm()
    form.show()
    form.name.setFocus()
    QTest.keyClick(form.name, Qt.Key.Key_Tab)
    app.processEvents()
    assert form.color.hasFocus()


def test_periodically_fixed_rate_keeps_independent_follow_on_index() -> None:
    _app()
    form = ScenarioForm()
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "3"),
        ("start_date", "2026-01-01"),
        ("as_of_date", "2025-12-31"),
        ("fixed_months", "1"),
        ("nominal_annual", "0.05"),
        ("index_annual", "0.03"),
        ("margin", "0.01"),
    ):
        form.fields[key].setText(value)
    form.rate_type.setCurrentIndex(form.rate_type.findData("periodic_variable"))
    assert form.calculate_button.isEnabled(), form.error_text
    _, rate, _, _ = form.build_inputs()
    assert isinstance(rate, PeriodicallyFixedRate)
    assert rate.initial_nominal_annual == Decimal("0.05")
    assert isinstance(rate.follow_on, VariableRate)
    assert rate.follow_on.observations[0].index_annual == Decimal("0.03")


def test_first_observation_must_match_index_shown_in_form() -> None:
    _app()
    form = ScenarioForm()
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "2"),
        ("start_date", "2026-01-01"),
        ("as_of_date", "2025-12-31"),
        ("index_annual", "0.05"),
        ("margin", "0.02"),
    ):
        form.fields[key].setText(value)
    form.rate_type.setCurrentIndex(form.rate_type.findData("variable"))
    form.add_rate_row()
    period = form.rate_path.item(0, 0)
    index = form.rate_path.item(0, 1)
    assert period is not None and index is not None
    period.setText("1")
    index.setText("0.06")
    assert not form.calculate_button.isEnabled()
    assert "indeks" in form.error_text.lower()


def test_invalid_input_clears_stale_derived_value_and_identifies_date() -> None:
    _app()
    form = ScenarioForm()
    form.fields["price"].setText("1200.00")
    form.fields["down_payment"].setText("200.00")
    assert form.fields["purchase_loan"].text() == "1000.00"

    form.fields["price"].setText("abc")
    assert form.fields["purchase_loan"].text() == ""
    assert form.origin_labels["purchase_loan"].text() == "Brak"

    form.fields["price"].setText("1200.00")
    form.fields["nominal_annual"].setText("0.12")
    form.fields["start_date"].setText("not-a-date")
    assert not form.calculate_button.isEnabled()
    assert "dat" in form.error_text.lower()
    assert "red" in form.fields["start_date"].styleSheet()
    assert form.fields["start_date"].accessibleDescription()


def test_extra_and_charge_after_term_are_rejected_before_calculation() -> None:
    _app()
    form = ScenarioForm()
    for key, value in (
        ("price", "1200.00"),
        ("down_payment", "200.00"),
        ("term_months", "2"),
        ("nominal_annual", "0.12"),
    ):
        form.fields[key].setText(value)
    form.add_extra_row()
    extra_period = form.one_time.item(0, 0)
    extra_amount = form.one_time.item(0, 1)
    assert extra_period is not None and extra_amount is not None
    extra_amount.setText("10.00")
    extra_period.setText("3")
    assert not form.calculate_button.isEnabled()
    assert "nadpłat" in form.error_text.lower()

    form.one_time.selectRow(0)
    form.remove_extra_row()
    form.add_charge_row()
    charge_period = form.charges.item(0, 6)
    assert charge_period is not None
    charge_period.setText("3")
    assert not form.calculate_button.isEnabled()
    assert "koszt" in form.error_text.lower()


def test_reopened_form_displays_stored_derivation_until_user_edits() -> None:
    _app()
    original = ScenarioForm()
    original.fields["price"].setText("1200.00")
    original.fields["down_payment"].setText("200.00")
    original.fields["nominal_annual"].setText("0.12")
    state = original.export_state()
    derived = original.derived_state()
    saved_loan = derived["purchase_loan"]
    assert isinstance(saved_loan, dict)
    saved_loan["value"] = "999.00"

    reopened = ScenarioForm()
    reopened.load_state(state, derived)
    assert reopened.fields["purchase_loan"].text() == "999.00"
    assert reopened.origin_labels["purchase_loan"].text() == "Wyliczone"

    reopened.fields["price"].setText("1300.00")
    assert reopened.fields["purchase_loan"].text() == "1100.00"
