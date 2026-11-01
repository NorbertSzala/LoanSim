"""Bidirectional input equations and provenance for core calculations."""

from decimal import Decimal, localcontext

import pytest

from loansim.core.derive import (
    derive_annuity_installment,
    derive_annuity_term,
    derive_property,
    derive_rate_components,
)


def test_property_values_derive_from_price_and_down_payment() -> None:
    result = derive_property(price=Decimal("100000.00"), down_payment=Decimal("20000.00"))

    assert result.purchase_loan.value == Decimal("80000.00")
    assert result.purchase_loan.origin == "derived"
    assert result.purchase_loan.inputs == ("price", "down_payment")
    assert result.price.origin == "entered"
    assert result.down_fraction.value == Decimal("0.2")
    assert result.ltv.value == Decimal("0.8")


def test_repeating_derived_fraction_does_not_create_a_false_money_conflict() -> None:
    result = derive_property(price=Decimal("3.00"), down_payment=Decimal("1.00"))

    assert result.down_fraction.value is not None
    assert result.purchase_loan.value == Decimal("2.00")
    assert result.down_payment.value == Decimal("1.00")


def test_property_derivation_is_independent_of_caller_decimal_precision() -> None:
    kwargs = {"price": Decimal("3.00"), "down_payment": Decimal("1.00")}
    reference = derive_property(**kwargs)

    with localcontext() as context:
        context.prec = 8
        altered = derive_property(**kwargs)

    assert altered == reference


def test_redundant_derived_ratios_do_not_invent_a_zero_price() -> None:
    result = derive_property(price=Decimal("297.25"), down_payment=Decimal("292.72"))

    assert result.price.value == Decimal("297.25")
    assert result.purchase_loan.value == Decimal("4.53")


def test_inconsistent_entered_fraction_and_ltv_are_rejected_without_financed_charges() -> None:
    with pytest.raises(ValueError, match="conflict"):
        derive_property(down_fraction=Decimal("0.2"), ltv=Decimal("0.9"))


def test_long_decimal_ltv_can_reconstruct_an_exact_cent_price() -> None:
    price = Decimal("636264.88")
    ltv = Decimal("0.34122963065319588282163239938687170663890799693360")

    result = derive_property(price=price, ltv=ltv, financed_charges=Decimal("761.33"))

    assert result.price.value == price
    assert result.purchase_loan.value is not None
    assert result.purchase_loan.value == result.purchase_loan.value.quantize(Decimal("0.01"))


@pytest.mark.parametrize(
    ("provided", "expected"),
    [
        ({"price": Decimal("100000.00"), "purchase_loan": Decimal("80000.00")}, "down_payment"),
        ({"down_payment": Decimal("20000.00"), "purchase_loan": Decimal("80000.00")}, "price"),
        ({"price": Decimal("100000.00"), "down_fraction": Decimal("0.2")}, "purchase_loan"),
        ({"price": Decimal("100000.00"), "ltv": Decimal("0.8")}, "down_payment"),
    ],
)
def test_each_property_member_can_be_derived(provided: dict[str, Decimal], expected: str) -> None:
    result = derive_property(**provided)

    assert getattr(result, expected).origin == "derived"
    assert result.price.value == Decimal("100000.00")
    assert result.down_payment.value == Decimal("20000.00")
    assert result.purchase_loan.value == Decimal("80000.00")


def test_financed_charge_raises_initial_ltv_without_changing_purchase_loan() -> None:
    result = derive_property(
        price=Decimal("100000.00"),
        down_payment=Decimal("20000.00"),
        financed_charges=Decimal("2000.00"),
    )

    assert result.purchase_loan.value == Decimal("80000.00")
    assert result.initial_debt.value == Decimal("82000.00")
    assert result.ltv.value == Decimal("0.82")


def test_down_payment_and_ltv_determine_price_with_financed_charge() -> None:
    result = derive_property(
        down_payment=Decimal("20000.00"),
        ltv=Decimal("0.82"),
        financed_charges=Decimal("2000.00"),
    )

    assert result.price.value == Decimal("100000.00")
    assert result.purchase_loan.value == Decimal("80000.00")


def test_down_fraction_and_ltv_determine_scale_only_with_financed_charge() -> None:
    determined = derive_property(
        down_fraction=Decimal("0.2"),
        ltv=Decimal("0.82"),
        financed_charges=Decimal("2000.00"),
    )
    underdetermined = derive_property(down_fraction=Decimal("0.2"), ltv=Decimal("0.8"))

    assert determined.price.value == Decimal("100000.00")
    assert underdetermined.price.value is None


def test_underdetermined_property_reports_missing_values() -> None:
    result = derive_property(price=Decimal("100000.00"))

    assert result.purchase_loan.value is None
    assert result.purchase_loan.reason == "insufficient independent inputs"


def test_conflicting_redundant_property_inputs_are_rejected() -> None:
    supplied = {
        "price": Decimal("100000.00"),
        "down_payment": Decimal("20000.00"),
        "purchase_loan": Decimal("70000.00"),
    }

    with pytest.raises(ValueError, match="conflict"):
        derive_property(**supplied)

    assert supplied["purchase_loan"] == Decimal("70000.00")


def test_rate_components_derive_missing_margin_without_future_observation() -> None:
    result = derive_rate_components(nominal_annual=Decimal("0.065"), index_annual=Decimal("0.05"))

    assert result.margin.value == Decimal("0.015")
    assert result.margin.origin == "derived"
    assert result.nominal_annual.origin == "entered"


def test_rate_components_reject_conflicting_redundancy() -> None:
    with pytest.raises(ValueError, match="conflict"):
        derive_rate_components(
            nominal_annual=Decimal("0.065"),
            index_annual=Decimal("0.05"),
            margin=Decimal("0.02"),
        )


def test_fixed_annuity_installment_is_derived_with_formula_provenance() -> None:
    result = derive_annuity_installment(Decimal("1000.00"), Decimal("0.12"), 2)

    assert result.value == Decimal("507.51")
    assert result.origin == "derived"
    assert result.inputs == ("initial_debt", "nominal_annual", "term_months")


def test_fixed_annuity_term_is_returned_only_when_unique_at_cent_precision() -> None:
    unique = derive_annuity_term(Decimal("1000.00"), Decimal("0.12"), Decimal("507.51"))
    ambiguous = derive_annuity_term(Decimal("1.00"), Decimal("0"), Decimal("0.01"))

    assert unique.months == 2
    assert unique.origin == "derived"
    assert ambiguous.months is None
    assert ambiguous.reason == "multiple terms produce the same rounded installment"


def test_term_derivation_rejects_non_amortizing_payment() -> None:
    with pytest.raises(ValueError, match="interest"):
        derive_annuity_term(Decimal("1000.00"), Decimal("0.12"), Decimal("10.00"))
