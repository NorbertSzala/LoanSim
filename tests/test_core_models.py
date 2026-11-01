"""Input-model boundaries for the approximate monthly engine."""

from dataclasses import FrozenInstanceError
from datetime import date
from decimal import Decimal

import pytest

from loansim.core.models import (
    Charge,
    ChargeCadence,
    ChargeCategory,
    ChargeFunding,
    ChargePayee,
    InstallmentType,
    LoanTerms,
    quantize_cent,
)


def test_round_half_up_at_a_cent_boundary() -> None:
    assert quantize_cent(Decimal("1.005")) == Decimal("1.01")
    assert quantize_cent(Decimal("1.004")) == Decimal("1.00")


def test_loan_terms_keep_explicit_purchase_financing_and_property_amounts() -> None:
    terms = LoanTerms(
        purchase_loan=Decimal("80000.00"),
        term_months=120,
        start_date=date(2026, 1, 31),
        installment_type=InstallmentType.ANNUITY,
        property_price=Decimal("100000.00"),
        down_payment=Decimal("20000.00"),
    )

    assert terms.purchase_loan == Decimal("80000.00")
    assert terms.currency == "PLN"
    with pytest.raises(FrozenInstanceError):
        terms.purchase_loan = Decimal("70000.00")  # type: ignore[misc]


@pytest.mark.parametrize(
    "change",
    [
        {"purchase_loan": 1000.0},
        {"purchase_loan": Decimal("1000.001")},
        {"purchase_loan": Decimal("0.00")},
        {"term_months": 0},
        {"currency": "EUR"},
        {"down_payment": Decimal("30000.00")},
    ],
)
def test_invalid_terms_are_rejected(change: dict[str, object]) -> None:
    values: dict[str, object] = {
        "purchase_loan": Decimal("80000.00"),
        "term_months": 120,
        "start_date": date(2026, 1, 31),
        "installment_type": InstallmentType.ANNUITY,
        "property_price": Decimal("100000.00"),
        "down_payment": Decimal("20000.00"),
    }
    values.update(change)

    with pytest.raises(ValueError):
        LoanTerms(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize("due_period", [0, 1])
def test_financed_recurring_charge_has_clear_validation_error(due_period: int) -> None:
    with pytest.raises(ValueError, match="Recurring charges.*paid from own funds"):
        Charge(
            Decimal("10.00"),
            ChargeCategory.MANDATORY_CREDIT,
            ChargeCadence.MONTHLY,
            ChargeFunding.FINANCED,
            ChargePayee.LENDER,
            due_period=due_period,
        )
