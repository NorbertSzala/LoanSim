"""Single-scenario inputs with explicit entered/derived provenance."""

import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any, Literal

from PySide6.QtCore import QSignalBlocker, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from loansim.core.derive import (
    DerivedValue,
    derive_annuity_installment,
    derive_annuity_term,
    derive_property,
    derive_rate_components,
)
from loansim.core.models import (
    ZERO,
    Charge,
    ChargeCadence,
    ChargeCategory,
    ChargeFunding,
    ChargePayee,
    ExtraPayment,
    InstallmentType,
    LoanTerms,
    OverpaymentPlan,
    OverpaymentResponse,
)
from loansim.core.rates import (
    FixedRate,
    PeriodicallyFixedRate,
    RateObservation,
    RatePlan,
    VariableRate,
)
from loansim.gui.strings import explain_derived, localize_core_error, tr, tr_list

_PROPERTY_KEYS = ("price", "down_payment", "purchase_loan", "down_fraction", "ltv")
_RATE_KEYS = ("nominal_annual", "index_annual", "margin")


def _number(text: str, name: str, *, required: bool = True) -> Decimal | None:
    if not text.strip():
        if required:
            raise ValueError(tr("required_number", name=name))
        return None
    try:
        value = Decimal(text.strip().replace(",", "."))
    except InvalidOperation as error:
        raise ValueError(tr("invalid_number", name=name)) from error
    if not value.is_finite():
        raise ValueError(tr("invalid_number", name=name))
    return value


def _integer(text: str, name: str) -> int:
    try:
        value = int(text.strip())
    except ValueError as error:
        raise ValueError(tr("invalid_integer", name=name)) from error
    if value < 1:
        raise ValueError(tr("positive_integer", name=name))
    return value


def _nonnegative_integer(text: str, name: str) -> int:
    try:
        value = int(text.strip())
    except ValueError as error:
        raise ValueError(tr("invalid_integer", name=name)) from error
    if value < 0:
        raise ValueError(tr("nonnegative_integer", name=name))
    return value


def _date(text: str, name: str) -> date:
    try:
        return date.fromisoformat(text.strip())
    except ValueError as error:
        raise ValueError(tr("invalid_date", name=name)) from error


def _table_text(table: QTableWidget, row: int, column: int) -> str:
    widget = table.cellWidget(row, column)
    if isinstance(widget, QComboBox):
        return str(widget.currentData())
    item = table.item(row, column)
    return item.text().strip() if item is not None else ""


class ScenarioForm(QWidget):
    """Never rewrites an entered field when an equation becomes inconsistent."""

    changed = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._updating = True
        self.fields: dict[str, QLineEdit] = {}
        self.locks: dict[str, QCheckBox] = {}
        self.origin_labels: dict[str, QLabel] = {}
        self._derived: dict[str, DerivedValue] = {}
        self.error_text = ""
        self.error_field: str | None = None
        layout = QVBoxLayout(self)
        self.name = self._simple("name", tr("default_scenario_name"))
        self.color = self._simple("color", "#3355AA")
        self.notes = QTextEdit()
        self.notes.setObjectName("notes")
        self.notes.setMaximumHeight(72)
        scenario = QGroupBox(tr("scenario"))
        scenario_form = QFormLayout(scenario)
        scenario_form.addRow(tr("name"), self.name)
        scenario_form.addRow(tr("color"), self.color)
        scenario_form.addRow(tr("notes"), self.notes)
        layout.addWidget(scenario)

        property_box = QGroupBox(tr("property"))
        property_form = QFormLayout(property_box)
        for key in _PROPERTY_KEYS:
            property_form.addRow(tr(key), self._derived_field(key))
        layout.addWidget(property_box)

        loan_box = QGroupBox(tr("loan"))
        loan_form = QFormLayout(loan_box)
        loan_form.addRow(tr("term_months"), self._derived_field("term_months"))
        self.fields["term_months"].setText("360")
        self.locks["term_months"].setChecked(True)
        loan_form.addRow(tr("start_date"), self._simple("start_date", date.today().isoformat()))
        self.installment_type = QComboBox()
        self.installment_type.setObjectName("installment_type")
        self.installment_type.addItem(tr("installment_annuity"), InstallmentType.ANNUITY)
        self.installment_type.addItem(tr("installment_declining"), InstallmentType.DECLINING)
        loan_form.addRow(tr("installment"), self.installment_type)
        loan_form.addRow(tr("entered_annuity"), self._derived_field("mandatory_installment"))
        self.annuity_payment = QLabel(tr("empty"))
        self.annuity_payment.setObjectName("annuity_payment")
        loan_form.addRow(tr("estimated_annuity"), self.annuity_payment)
        layout.addWidget(loan_box)

        rate_box = QGroupBox(tr("rate"))
        rate_form = QFormLayout(rate_box)
        self.rate_type = QComboBox()
        self.rate_type.setObjectName("rate_type")
        for label, value in (
            (tr("rate_fixed"), "fixed"),
            (tr("rate_variable"), "variable"),
            (tr("rate_periodic_fixed"), "periodic_fixed"),
            (tr("rate_periodic_variable"), "periodic_variable"),
        ):
            self.rate_type.addItem(label, value)
        rate_form.addRow(tr("rate_type"), self.rate_type)
        for key in _RATE_KEYS:
            rate_form.addRow(tr(key), self._derived_field(key))
        for key, default in (
            ("index_name", tr("manual_index")),
            ("fixed_months", "60"),
            ("follow_on_nominal", "0.07"),
            ("as_of_date", date.today().isoformat()),
        ):
            rate_form.addRow(tr(key), self._simple(key, default))
        self.rate_path = QTableWidget(0, 6)
        self.rate_path.setObjectName("rate_path")
        self.rate_path.setHorizontalHeaderLabels(tr_list("rate_path_headers"))
        rate_form.addRow(tr("rate_path"), self.rate_path)
        add_rate = QPushButton(tr("add_rate"))
        add_rate.clicked.connect(self.add_rate_row)
        rate_form.addRow(add_rate)
        remove_rate = QPushButton(tr("remove_rate"))
        remove_rate.clicked.connect(self.remove_rate_row)
        rate_form.addRow(remove_rate)
        layout.addWidget(rate_box)

        extra_box = QGroupBox(tr("overpayments"))
        extra_form = QFormLayout(extra_box)
        extra_form.addRow(tr("regular_extra"), self._simple("regular_extra", "0.00"))
        extra_form.addRow(tr("monthly_cap"), self._simple("monthly_cap"))
        self.response = QComboBox()
        self.response.addItem(tr("response_shorten"), OverpaymentResponse.SHORTEN_TERM)
        self.response.addItem(tr("response_lower"), OverpaymentResponse.LOWER_INSTALLMENT)
        extra_form.addRow(tr("response"), self.response)
        self.one_time = QTableWidget(0, 2)
        self.one_time.setObjectName("one_time")
        self.one_time.setHorizontalHeaderLabels(tr_list("one_time_headers"))
        extra_form.addRow(tr("one_time"), self.one_time)
        add_extra = QPushButton(tr("add_extra"))
        add_extra.clicked.connect(self.add_extra_row)
        extra_form.addRow(add_extra)
        remove_extra = QPushButton(tr("remove_extra"))
        remove_extra.clicked.connect(self.remove_extra_row)
        extra_form.addRow(remove_extra)
        layout.addWidget(extra_box)

        charge_box = QGroupBox(tr("charges"))
        charge_form = QFormLayout(charge_box)
        self.charges = QTableWidget(0, 8)
        self.charges.setObjectName("charges")
        self.charges.setHorizontalHeaderLabels(tr_list("charge_headers"))
        charge_form.addRow(self.charges)
        add_charge = QPushButton(tr("add_charge"))
        add_charge.clicked.connect(self.add_charge_row)
        charge_form.addRow(add_charge)
        remove_charge = QPushButton(tr("remove_charge"))
        remove_charge.setObjectName("remove_charge")
        remove_charge.clicked.connect(self.remove_charge_row)
        charge_form.addRow(remove_charge)
        layout.addWidget(charge_box)

        self.error_label = QLabel()
        self.error_label.setObjectName("validation_error")
        self.error_label.setAccessibleName(tr("validation_error"))
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #a31b1b")
        layout.addWidget(self.error_label)
        self.calculate_button = QPushButton(tr("calculate"))
        self.calculate_button.setObjectName("calculate")
        layout.addWidget(self.calculate_button)

        for combo in (self.installment_type, self.rate_type, self.response):
            combo.currentIndexChanged.connect(self.recalculate)
        for key, field in self.fields.items():
            field.textChanged.connect(lambda _text, name=key: self._field_changed(name))
        self.notes.textChanged.connect(self.changed.emit)
        for table in (self.rate_path, self.one_time, self.charges):
            table.itemChanged.connect(self.recalculate)
        self._updating = False
        self.recalculate()

    def _simple(self, key: str, default: str = "") -> QLineEdit:
        field = QLineEdit(default)
        field.setObjectName(key)
        self.fields[key] = field
        return field

    def _derived_field(self, key: str) -> QWidget:
        container = QWidget()
        line = QHBoxLayout(container)
        line.setContentsMargins(0, 0, 0, 0)
        field = self._simple(key)
        lock = QCheckBox(tr("lock"))
        lock.setObjectName(f"lock_{key}")
        lock.toggled.connect(lambda checked, name=key: self._lock_changed(name, checked))
        self.locks[key] = lock
        origin = QLabel(tr("origin_missing"))
        origin.setObjectName(f"origin_{key}")
        origin.setMinimumWidth(85)
        self.origin_labels[key] = origin
        line.addWidget(field)
        line.addWidget(origin)
        line.addWidget(lock)
        return container

    def _field_changed(self, key: str) -> None:
        if self._updating:
            return
        if key in self.locks:
            with QSignalBlocker(self.locks[key]):
                self.locks[key].setChecked(bool(self.fields[key].text().strip()))
            self.fields[key].setReadOnly(False)
        self.recalculate()

    def _lock_changed(self, key: str, checked: bool) -> None:
        if self._updating:
            return
        if not checked:
            with QSignalBlocker(self.fields[key]):
                self.fields[key].clear()
        self.origin_labels[key].setText(tr("origin_entered") if checked else tr("origin_missing"))
        self.fields[key].setReadOnly(False)
        self.recalculate()

    def _entered(self, key: str) -> Decimal | None:
        return (
            _number(self.fields[key].text(), key, required=False)
            if self.locks[key].isChecked()
            else None
        )

    def _show_derived(self, key: str, value: DerivedValue) -> None:
        self._derived[key] = value
        field = self.fields[key]
        if self.locks[key].isChecked():
            self.origin_labels[key].setText(tr("origin_entered"))
            field.setToolTip(tr("locked_tooltip"))
            field.setReadOnly(False)
            return
        with QSignalBlocker(field):
            field.setText(format(value.value, "f") if value.value is not None else "")
        field.setReadOnly(value.value is not None)
        field.setToolTip(explain_derived(value.formula or value.reason))
        self.origin_labels[key].setText(
            tr("origin_derived") if value.value is not None else tr("origin_missing")
        )

    def recalculate(self) -> None:
        if self._updating:
            return
        self._updating = True
        self.error_field = None
        try:
            self._derived.clear()
            for key in self.locks:
                if not self.locks[key].isChecked():
                    self._show_derived(key, DerivedValue(None, "missing"))
            for key in self.locks:
                if self.locks[key].isChecked():
                    self._show_derived(key, DerivedValue(self._entered(key), "entered"))
            charges = self._parse_charges()
            financed = sum(
                (charge.amount for charge in charges if charge.funding is ChargeFunding.FINANCED),
                ZERO,
            )
            property_values = derive_property(
                price=self._entered("price"),
                down_payment=self._entered("down_payment"),
                purchase_loan=self._entered("purchase_loan"),
                down_fraction=self._entered("down_fraction"),
                ltv=self._entered("ltv"),
                financed_charges=financed,
            )
            for key in _PROPERTY_KEYS:
                self._show_derived(key, getattr(property_values, key))
            rate_kind = self.rate_type.currentData()
            if str(rate_kind).startswith("periodic"):
                for key in _RATE_KEYS:
                    entered = self._entered(key)
                    self._show_derived(
                        key,
                        DerivedValue(
                            entered,
                            "entered" if entered is not None else "missing",
                            reason=None if entered is not None else tr("rate_requires_user"),
                        ),
                    )
                nominal_value = self._entered("nominal_annual")
            else:
                rate_values = derive_rate_components(
                    nominal_annual=self._entered("nominal_annual"),
                    index_annual=self._entered("index_annual"),
                    margin=self._entered("margin"),
                )
                for key in _RATE_KEYS:
                    self._show_derived(key, getattr(rate_values, key))
                nominal_value = rate_values.nominal_annual.value
            debt = property_values.initial_debt.value
            if (
                debt is not None
                and nominal_value is not None
                and self.rate_type.currentData() == "fixed"
                and self.installment_type.currentData() == InstallmentType.ANNUITY
            ):
                payment = self._entered("mandatory_installment")
                term_text = self.fields["term_months"].text().strip()
                if not term_text and payment is not None:
                    term_result = derive_annuity_term(debt, nominal_value, payment)
                    if term_result.months is None:
                        raise ValueError(term_result.reason or tr("term_not_determinable"))
                    self._show_derived(
                        "term_months",
                        DerivedValue(
                            Decimal(term_result.months),
                            "derived",
                            tr("term_formula"),
                            ("mandatory_installment", "nominal_annual", "purchase_loan"),
                        ),
                    )
                if self.fields["term_months"].text().strip():
                    term = _integer(self.fields["term_months"].text(), "okres kredytu")
                    expected = derive_annuity_installment(debt, nominal_value, term)
                    if payment is not None and expected.value != payment:
                        raise ValueError(tr("payment_conflict"))
                    self._show_derived("mandatory_installment", expected)
            elif not self.locks["mandatory_installment"].isChecked():
                self._show_derived(
                    "mandatory_installment",
                    DerivedValue(None, "missing", reason=tr("payment_requires_fixed")),
                )
            self.error_text = ""
            self.error_field = None
            try:
                terms, rate, _, _ = self.build_inputs()
                if (
                    isinstance(rate, FixedRate)
                    and terms.installment_type is InstallmentType.ANNUITY
                ):
                    initial_debt = property_values.initial_debt.value
                    assert initial_debt is not None
                    annuity = derive_annuity_installment(
                        initial_debt,
                        rate.nominal_annual,
                        terms.term_months,
                    )
                    self.annuity_payment.setText(str(annuity.value))
                    self.annuity_payment.setToolTip(explain_derived(annuity.formula))
                else:
                    self.annuity_payment.setText(tr("empty"))
            except ValueError as error:
                self.error_text, self.error_field = localize_core_error(str(error))
                self.annuity_payment.setText(tr("empty"))
        except ValueError as error:
            self.error_text, self.error_field = localize_core_error(str(error))
            self.annuity_payment.setText(tr("empty"))
        finally:
            self.error_field = self.error_field or self._error_target(self.error_text)
            self.error_label.setText(self.error_text)
            self.calculate_button.setEnabled(not self.error_text)
            self._decorate_error()
            self._updating = False
            self.changed.emit()

    def _decorate_error(self) -> None:
        targets: dict[str, QWidget] = {
            **self.fields,
            "rate_path": self.rate_path,
            "one_time": self.one_time,
            "charges": self.charges,
        }
        for field in targets.values():
            field.setStyleSheet("")
            field.setAccessibleDescription("")
        if self.error_field in targets:
            field = targets[self.error_field]
            field.setStyleSheet("border: 2px solid red")
            field.setAccessibleDescription(self.error_text)

    def _error_target(self, message: str) -> str | None:
        if not message:
            return None
        for key in (*self.fields, "rate_path", "one_time", "charges"):
            if message.startswith(f"{key}:") or key in message:
                return key
        aliases = {
            "purchase_loan": "kwota kredytu",
            "term_months": "okres kredytu",
            "nominal_annual": "stopa nominalna",
            "down_payment": "wkład",
            "mandatory_installment": "rata",
            "index_annual": "indeks",
            "one_time": "nadpłat",
            "charges": "koszt",
            "monthly_cap": "limit miesięczny",
            "start_date": "data",
            "regular_extra": "stała nadpłata",
            "margin": "marża",
            "follow_on_nominal": "stopa po okresie stałym",
            "fixed_months": "okres stały",
        }
        for key, alias in sorted(aliases.items(), key=lambda item: len(item[1]), reverse=True):
            if alias in message.lower():
                return key
        return None

    def set_external_error(self, message: str, field: str | None = None) -> None:
        self.error_text = message
        self.error_field = field or self._error_target(message)
        self.error_label.setText(message)
        self.calculate_button.setEnabled(False)
        self._decorate_error()

    def _rate_observations(
        self, first_period: int, first_index: Decimal | None
    ) -> tuple[RateObservation, ...]:
        observations: list[RateObservation] = []
        for row in range(self.rate_path.rowCount()):
            period = _integer(_table_text(self.rate_path, row, 0), "rate_path: okres indeksu")
            index = _number(_table_text(self.rate_path, row, 1), "rate_path: indeks")
            assert index is not None
            kind_text = _table_text(self.rate_path, row, 2) or "hypothetical"
            if kind_text not in ("historical", "hypothetical"):
                raise ValueError(tr("invalid_observation_kind"))
            kind: Literal["historical", "hypothetical"] = (
                "historical" if kind_text == "historical" else "hypothetical"
            )
            source = _table_text(self.rate_path, row, 3) or tr("manual_source")
            observed = _table_text(self.rate_path, row, 4)
            published = _table_text(self.rate_path, row, 5)
            observations.append(
                RateObservation(
                    period,
                    index,
                    kind,
                    source,
                    observed_on=_date(observed, "rate_path") if observed else None,
                    published_on=_date(published, "rate_path") if published else None,
                )
            )
        if not any(point.period == first_period for point in observations):
            if first_index is None:
                raise ValueError(tr("missing_first_index"))
            observations.insert(
                0, RateObservation(first_period, first_index, "hypothetical", tr("manual_source"))
            )
        elif first_index is not None and any(
            point.period == first_period and point.index_annual != first_index
            for point in observations
        ):
            raise ValueError(tr("first_index_conflict"))
        return tuple(observations)

    def build_inputs(self) -> tuple[LoanTerms, RatePlan, OverpaymentPlan, tuple[Charge, ...]]:
        """Build only validated core objects; all formulas remain in `core`."""
        if not self.name.text().strip():
            raise ValueError(tr("name_required"))
        if re.fullmatch(r"#[0-9a-fA-F]{6}", self.color.text()) is None:
            raise ValueError(tr("color_format"))
        loan = _number(self.fields["purchase_loan"].text(), "kwota kredytu")
        assert loan is not None
        price = _number(self.fields["price"].text(), "cena", required=False)
        down = _number(self.fields["down_payment"].text(), "wkład", required=False)
        if price is None or down is None:
            price = down = None
        term = _integer(self.fields["term_months"].text(), "okres kredytu")
        terms = LoanTerms(
            loan,
            term,
            _date(self.fields["start_date"].text(), "start_date"),
            InstallmentType(self.installment_type.currentData()),
            property_price=price,
            down_payment=down,
        )
        rate_kind = self.rate_type.currentData()
        nominal = _number(self.fields["nominal_annual"].text(), "stopa nominalna", required=False)
        index = _number(self.fields["index_annual"].text(), "indeks", required=False)
        margin = _number(self.fields["margin"].text(), "marża", required=False)
        if rate_kind == "fixed":
            if nominal is None:
                raise ValueError(tr("nominal_missing"))
            rate: RatePlan = FixedRate(nominal, tr("manual_source"))
        else:
            if rate_kind.startswith("periodic"):
                if nominal is None:
                    raise ValueError(tr("periodic_nominal_missing"))
                fixed_months = _integer(self.fields["fixed_months"].text(), "okres stały")
            else:
                fixed_months = 0
            if rate_kind == "periodic_fixed":
                assert nominal is not None
                follow = _number(self.fields["follow_on_nominal"].text(), "stopa po okresie stałym")
                assert follow is not None
                rate = PeriodicallyFixedRate(
                    nominal, fixed_months, FixedRate(follow, tr("follow_on_source"))
                )
            else:
                if margin is None:
                    raise ValueError(tr("margin_missing"))
                if fixed_months:
                    assert nominal is not None
                first = fixed_months + 1
                variable = VariableRate(
                    self.fields["index_name"].text().strip(),
                    margin,
                    self._rate_observations(first, index),
                    _date(self.fields["as_of_date"].text(), "as_of_date"),
                )
                if fixed_months:
                    assert nominal is not None
                    rate = PeriodicallyFixedRate(nominal, fixed_months, variable)
                else:
                    rate = variable
        regular = _number(self.fields["regular_extra"].text(), "stała nadpłata")
        cap = _number(self.fields["monthly_cap"].text(), "limit miesięczny", required=False)
        assert regular is not None
        extras = []
        for row in range(self.one_time.rowCount()):
            amount = _number(_table_text(self.one_time, row, 1), "one_time: nadpłata")
            assert amount is not None
            extras.append(
                ExtraPayment(
                    _integer(_table_text(self.one_time, row, 0), "one_time: okres nadpłaty"),
                    amount,
                )
            )
        plan = OverpaymentPlan(
            OverpaymentResponse(self.response.currentData()), regular, tuple(extras), cap
        )
        if any(extra.period > term for extra in plan.one_time):
            raise ValueError(tr("extra_after_term"))
        charges = self._parse_charges()
        if any(
            charge.due_period > term
            or (charge.last_period is not None and charge.last_period > term)
            for charge in charges
        ):
            raise ValueError(tr("charge_after_term"))
        return terms, rate, plan, charges

    def _parse_charges(self) -> tuple[Charge, ...]:
        charges = []
        for row in range(self.charges.rowCount()):
            amount = _number(_table_text(self.charges, row, 1), "charges: koszt")
            assert amount is not None
            category = ChargeCategory(_table_text(self.charges, row, 2))
            cadence = ChargeCadence(_table_text(self.charges, row, 3))
            funding = ChargeFunding(_table_text(self.charges, row, 4))
            payee = ChargePayee(_table_text(self.charges, row, 5))
            due = _nonnegative_integer(
                _table_text(self.charges, row, 6) or "0", "charges: okres kosztu"
            )
            last_text = _table_text(self.charges, row, 7)
            charges.append(
                Charge(
                    amount,
                    category,
                    cadence,
                    funding,
                    payee,
                    due,
                    _integer(last_text, "charges: koniec kosztu") if last_text else None,
                    _table_text(self.charges, row, 0),
                )
            )
        return tuple(charges)

    def add_rate_row(self) -> None:
        row = self.rate_path.rowCount()
        self._updating = True
        self.rate_path.insertRow(row)
        for column, value in enumerate(
            (str(row + 2), "", "hypothetical", tr("manual_source"), "", "")
        ):
            self._set_table_value(self.rate_path, row, column, value)
        self._updating = False
        self.recalculate()

    def add_extra_row(self) -> None:
        row = self.one_time.rowCount()
        self._updating = True
        self.one_time.insertRow(row)
        for column, value in enumerate(("1", "0.00")):
            self._set_table_value(self.one_time, row, column, value)
        self._updating = False
        self.recalculate()

    def add_charge_row(self) -> None:
        row = self.charges.rowCount()
        self._updating = True
        self.charges.insertRow(row)
        defaults = (
            tr("default_charge_name"),
            "100.00",
            "mandatory_credit",
            "once",
            "own_funds",
            "lender",
            "0",
            "",
        )
        for column, value in enumerate(defaults):
            self._set_table_value(self.charges, row, column, value)
        self._updating = False
        self.recalculate()

    def _set_table_value(self, table: QTableWidget, row: int, column: int, value: str) -> None:
        choices: tuple[tuple[str, str], ...] | None = None
        if table is self.rate_path and column == 2:
            choices = (
                (tr("observation_hypothetical"), "hypothetical"),
                (tr("observation_historical"), "historical"),
            )
        elif table is self.charges:
            by_column = {
                2: (
                    (tr("charge_mandatory"), "mandatory_credit"),
                    (tr("charge_optional"), "optional_credit"),
                    (tr("charge_acquisition"), "acquisition"),
                ),
                3: ((tr("cadence_once"), "once"), (tr("cadence_monthly"), "monthly")),
                4: ((tr("funding_own"), "own_funds"), (tr("funding_financed"), "financed")),
                5: ((tr("payee_lender"), "lender"), (tr("payee_other"), "other")),
            }
            choices = by_column.get(column)
        if choices is None:
            table.setItem(row, column, QTableWidgetItem(value))
            return
        combo = QComboBox()
        for label, code in choices:
            combo.addItem(label, code)
        selected = combo.findData(value)
        if selected < 0:
            raise ValueError(tr("unknown_saved_choice"))
        combo.setCurrentIndex(selected)
        combo.currentIndexChanged.connect(self.recalculate)
        table.setCellWidget(row, column, combo)

    def _remove_row(self, table: QTableWidget) -> None:
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)
            self.recalculate()

    def remove_rate_row(self) -> None:
        self._remove_row(self.rate_path)

    def remove_extra_row(self) -> None:
        self._remove_row(self.one_time)

    def remove_charge_row(self) -> None:
        self._remove_row(self.charges)

    def export_state(self) -> dict[str, object]:
        """Preserve exactly what the user entered, including locks and table rows."""
        return {
            "fields": {
                key: field.text()
                for key, field in self.fields.items()
                if key not in self.locks or self.locks[key].isChecked()
            },
            "locks": [key for key, lock in self.locks.items() if lock.isChecked()],
            "installment_type": self.installment_type.currentData(),
            "rate_type": self.rate_type.currentData(),
            "response": self.response.currentData(),
            "notes": self.notes.toPlainText(),
            "rate_path": self._table_state(self.rate_path),
            "one_time": self._table_state(self.one_time),
            "charges": self._table_state(self.charges),
        }

    @staticmethod
    def _table_state(table: QTableWidget) -> list[list[str]]:
        return [
            [_table_text(table, row, column) for column in range(table.columnCount())]
            for row in range(table.rowCount())
        ]

    def load_state(
        self, state: dict[str, Any], derived_state: dict[str, object] | None = None
    ) -> None:
        previous_state = self.export_state()
        previous_derived = self.derived_state()
        previous_error = self.error_text
        previous_error_field = self.error_field
        previous_calculate_enabled = self.calculate_button.isEnabled()
        try:
            self._apply_state(state, derived_state)
        except Exception as error:
            self._apply_state(previous_state, previous_derived)
            self.error_text = previous_error
            self.error_field = previous_error_field
            self.error_label.setText(previous_error)
            self.calculate_button.setEnabled(previous_calculate_enabled)
            self._decorate_error()
            raise ValueError(tr("invalid_saved_state")) from error

    def _apply_state(self, state: dict[str, Any], derived_state: dict[str, object] | None) -> None:
        self._updating = True
        try:
            for key, field in self.fields.items():
                field.setText(state.get("fields", {}).get(key, ""))
            for key, lock in self.locks.items():
                lock.setChecked(key in state.get("locks", []))
            for combo, key in (
                (self.installment_type, "installment_type"),
                (self.rate_type, "rate_type"),
                (self.response, "response"),
            ):
                index = combo.findData(state[key])
                if index < 0:
                    raise ValueError(tr("unknown_saved_choice"))
                combo.setCurrentIndex(index)
            self.notes.setPlainText(state.get("notes", ""))
            for table, key in (
                (self.rate_path, "rate_path"),
                (self.one_time, "one_time"),
                (self.charges, "charges"),
            ):
                table.setRowCount(0)
                for values in state.get(key, []):
                    row = table.rowCount()
                    table.insertRow(row)
                    for column, value in enumerate(values):
                        self._set_table_value(table, row, column, value)
        finally:
            self._updating = False
        if derived_state is None:
            self.recalculate()
            return
        self.restore_derived_state(derived_state)

    def restore_derived_state(self, state: dict[str, object]) -> None:
        """Display saved provenance without invoking the current calculation engine."""
        self._derived.clear()
        for key in self.locks:
            stored = state.get(key)
            if not isinstance(stored, dict):
                derived = DerivedValue(None, "missing")
            else:
                raw_value = stored.get("value")
                if raw_value is not None and not isinstance(raw_value, str):
                    raise ValueError(tr("invalid_saved_derived"))
                value = _number(raw_value, key, required=False) if raw_value is not None else None
                raw_origin = stored.get("origin")
                if raw_origin not in ("entered", "derived", "missing"):
                    raise ValueError(tr("invalid_saved_origin"))
                origin: Literal["entered", "derived", "missing"] = raw_origin
                formula = stored.get("formula")
                reason = stored.get("reason")
                raw_inputs = stored.get("inputs", [])
                if (
                    (formula is not None and not isinstance(formula, str))
                    or (reason is not None and not isinstance(reason, str))
                    or not isinstance(raw_inputs, list)
                    or not all(isinstance(item, str) for item in raw_inputs)
                ):
                    raise ValueError(tr("invalid_saved_provenance"))
                derived = DerivedValue(value, origin, formula, tuple(raw_inputs), reason)
            self._show_derived(key, derived)
        payment = self._derived.get("mandatory_installment")
        self.annuity_payment.setText(
            str(payment.value)
            if payment is not None
            and payment.value is not None
            and self.rate_type.currentData() == "fixed"
            and self.installment_type.currentData() == InstallmentType.ANNUITY
            else tr("empty")
        )
        self.error_text = ""
        self.error_field = None
        self.error_label.clear()
        self.calculate_button.setEnabled(True)
        self._decorate_error()
        self.changed.emit()

    def derived_state(self) -> dict[str, object]:
        return {
            key: {
                "value": str(value.value) if value.value is not None else None,
                "origin": "entered" if self.locks[key].isChecked() else value.origin,
                "formula": value.formula,
                "inputs": list(value.inputs),
                "reason": value.reason,
            }
            for key, value in self._derived.items()
        }
