"""Independent cost-category and cash-flow reconciliation cases."""

from datetime import date
from decimal import Decimal

import pytest

from loansim.core.amortization import simulate
from loansim.core.models import (
    Charge,
    ChargeCadence,
    ChargeCategory,
    ChargeFunding,
    ChargePayee,
    InstallmentType,
    LoanTerms,
    OverpaymentPlan,
    OverpaymentResponse,
)
from loansim.core.rates import FixedRate


def _terms() -> LoanTerms:
    return LoanTerms(
        Decimal("1000.00"),
        2,
        date(2026, 1, 1),
        InstallmentType.ANNUITY,
        property_price=Decimal("1200.00"),
        down_payment=Decimal("200.00"),
    )


def test_upfront_own_funds_credit_charge_is_paid_once() -> None:
    charge = Charge(
        Decimal("100.00"),
        ChargeCategory.MANDATORY_CREDIT,
        ChargeCadence.ONCE,
        ChargeFunding.OWN_FUNDS,
        ChargePayee.LENDER,
    )
    result = simulate(_terms(), FixedRate(Decimal("0")), charges=(charge,))

    assert result.initial_debt == Decimal("1000.00")
    assert result.total_financing_charges == Decimal("100.00")
    assert result.total_recurring_charges == Decimal("0.00")
    assert result.financing_cost == Decimal("100.00")
    assert result.total_nominal_loan_cost == Decimal("100.00")
    assert result.total_lender_repayments == Decimal("1100.00")
    assert result.total_cash_outflow == Decimal("1100.00")
    assert result.acquisition_date_own_funds == Decimal("300.00")
    assert result.lifetime_buyer_cash_outflow == Decimal("1300.00")


def test_financed_one_time_charge_increases_debt_without_double_cash_count() -> None:
    charge = Charge(
        Decimal("100.00"),
        ChargeCategory.MANDATORY_CREDIT,
        ChargeCadence.ONCE,
        ChargeFunding.FINANCED,
        ChargePayee.LENDER,
    )
    result = simulate(_terms(), FixedRate(Decimal("0")), charges=(charge,))

    assert result.initial_debt == Decimal("1100.00")
    assert [row.actual_cash_outflow for row in result.rows] == [Decimal("550.00")] * 2
    assert result.total_financing_charges == Decimal("100.00")
    assert result.total_lender_repayments == Decimal("1100.00")
    assert result.total_cash_outflow == Decimal("1100.00")
    assert result.ltv is not None
    assert abs(result.ltv * Decimal("1200.00") - Decimal("1100.00")) < Decimal("1e-20")
    assert result.lifetime_buyer_cash_outflow == Decimal("1300.00")


def test_financed_one_time_charge_accrues_interest_on_added_debt() -> None:
    charge = Charge(
        Decimal("100.00"),
        ChargeCategory.MANDATORY_CREDIT,
        ChargeCadence.ONCE,
        ChargeFunding.FINANCED,
        ChargePayee.LENDER,
    )
    result = simulate(
        LoanTerms(Decimal("1000.00"), 1, date(2026, 1, 1), InstallmentType.ANNUITY),
        FixedRate(Decimal("0.12")),
        charges=(charge,),
    )

    assert result.initial_debt == Decimal("1100.00")
    assert result.total_interest == Decimal("11.00")
    assert result.financing_cost == Decimal("111.00")
    assert result.total_cash_outflow == Decimal("1111.00")


def test_acquisition_charge_is_separate_from_financing_cost() -> None:
    charge = Charge(
        Decimal("50.00"),
        ChargeCategory.ACQUISITION,
        ChargeCadence.ONCE,
        ChargeFunding.OWN_FUNDS,
        ChargePayee.OTHER,
    )
    result = simulate(_terms(), FixedRate(Decimal("0")), charges=(charge,))

    assert result.total_financing_charges == Decimal("0.00")
    assert result.total_property_acquisition_cost == Decimal("1250.00")
    assert result.acquisition_date_own_funds == Decimal("250.00")
    assert result.lifetime_buyer_cash_outflow == Decimal("1250.00")


def test_financed_acquisition_charge_is_not_counted_as_credit_fee_or_upfront_cash() -> None:
    charge = Charge(
        Decimal("50.00"),
        ChargeCategory.ACQUISITION,
        ChargeCadence.ONCE,
        ChargeFunding.FINANCED,
        ChargePayee.OTHER,
    )
    result = simulate(_terms(), FixedRate(Decimal("0")), charges=(charge,))

    assert result.initial_debt == Decimal("1050.00")
    assert result.total_financing_charges == Decimal("0.00")
    assert result.total_property_acquisition_cost == Decimal("1250.00")
    assert result.acquisition_date_own_funds == Decimal("200.00")
    assert result.total_cash_outflow == Decimal("1050.00")
    assert result.lifetime_buyer_cash_outflow == Decimal("1250.00")


def test_recurring_own_funds_fee_is_in_each_payment_and_not_lender_total() -> None:
    charge = Charge(
        Decimal("10.00"),
        ChargeCategory.OPTIONAL_CREDIT,
        ChargeCadence.MONTHLY,
        ChargeFunding.OWN_FUNDS,
        ChargePayee.OTHER,
        due_period=1,
    )
    result = simulate(_terms(), FixedRate(Decimal("0")), charges=(charge,))

    assert [row.charge_outflow for row in result.rows] == [Decimal("10.00")] * 2
    assert [row.actual_cash_outflow for row in result.rows] == [Decimal("510.00")] * 2
    assert result.total_financing_charges == Decimal("20.00")
    assert result.total_lender_repayments == Decimal("1000.00")
    assert result.total_cash_outflow == Decimal("1020.00")
    assert result.total_recurring_charges == Decimal("20.00")
    assert [event.cash_outflow for event in result.charge_events] == [
        Decimal("10.00"),
        Decimal("10.00"),
    ]


def test_financed_origination_fee_and_recurring_own_funds_fee_are_not_double_counted() -> None:
    financed = Charge(
        Decimal("100.00"),
        ChargeCategory.MANDATORY_CREDIT,
        ChargeCadence.ONCE,
        ChargeFunding.FINANCED,
        ChargePayee.LENDER,
    )
    recurring = Charge(
        Decimal("10.00"),
        ChargeCategory.OPTIONAL_CREDIT,
        ChargeCadence.MONTHLY,
        ChargeFunding.OWN_FUNDS,
        ChargePayee.OTHER,
        due_period=1,
    )

    result = simulate(_terms(), FixedRate(Decimal("0")), charges=(financed, recurring))

    assert result.initial_debt == Decimal("1100.00")
    assert [row.mandatory_payment for row in result.rows] == [Decimal("550.00")] * 2
    assert [row.actual_cash_outflow for row in result.rows] == [Decimal("560.00")] * 2
    assert result.total_recurring_charges == Decimal("20.00")
    assert result.total_financing_charges == Decimal("120.00")
    assert result.financing_cost == Decimal("120.00")
    assert result.total_lender_repayments == Decimal("1100.00")
    assert result.total_cash_outflow == Decimal("1120.00")
    assert result.lifetime_buyer_cash_outflow == Decimal("1320.00")
    assert [event.cash_outflow for event in result.charge_events] == [
        Decimal("0.00"),
        Decimal("10.00"),
        Decimal("10.00"),
    ]


def test_mixed_charge_schedule_matches_independent_rational_reference() -> None:
    """Expected cents were calculated separately with exact rational arithmetic."""
    financed = Charge(
        Decimal("100.00"),
        ChargeCategory.MANDATORY_CREDIT,
        ChargeCadence.ONCE,
        ChargeFunding.FINANCED,
        ChargePayee.LENDER,
    )
    recurring = Charge(
        Decimal("10.00"),
        ChargeCategory.OPTIONAL_CREDIT,
        ChargeCadence.MONTHLY,
        ChargeFunding.OWN_FUNDS,
        ChargePayee.OTHER,
        due_period=1,
    )

    result = simulate(_terms(), FixedRate(Decimal("0.12")), charges=(financed, recurring))

    assert [
        (row.interest, row.actual_cash_outflow, row.closing_balance) for row in result.rows
    ] == [
        (Decimal("11.00"), Decimal("568.26"), Decimal("552.74")),
        (Decimal("5.53"), Decimal("568.27"), Decimal("0.00")),
    ]
    assert result.total_interest == Decimal("16.53")
    assert result.total_recurring_charges == Decimal("20.00")
    assert result.financing_cost == Decimal("136.53")
    assert result.total_cash_outflow == Decimal("1136.53")
    assert result.lifetime_buyer_cash_outflow == Decimal("1336.53")


def test_recurring_charge_is_only_incurred_until_early_payoff() -> None:
    charge = Charge(
        Decimal("10.00"),
        ChargeCategory.MANDATORY_CREDIT,
        ChargeCadence.MONTHLY,
        ChargeFunding.OWN_FUNDS,
        ChargePayee.OTHER,
        due_period=1,
    )
    plan = OverpaymentPlan(
        OverpaymentResponse.SHORTEN_TERM,
        monthly_cap=Decimal("1010.00"),
    )

    result = simulate(_terms(), FixedRate(Decimal("0")), plan, charges=(charge,))

    assert result.effective_months == 1
    assert result.rows[0].actual_cash_outflow == Decimal("1010.00")
    assert result.rows[0].closing_balance == Decimal("0.00")
    assert result.total_recurring_charges == Decimal("10.00")
    assert result.total_financing_charges == Decimal("10.00")
    assert result.total_cash_outflow == Decimal("1010.00")


def test_combined_payment_cap_includes_recurring_charge_before_extra_principal() -> None:
    charge = Charge(
        Decimal("10.00"),
        ChargeCategory.OPTIONAL_CREDIT,
        ChargeCadence.MONTHLY,
        ChargeFunding.OWN_FUNDS,
        ChargePayee.OTHER,
        due_period=1,
    )
    plan = OverpaymentPlan(OverpaymentResponse.SHORTEN_TERM, monthly_cap=Decimal("600.00"))
    result = simulate(_terms(), FixedRate(Decimal("0")), plan, charges=(charge,))

    assert result.rows[0].mandatory_payment == Decimal("500.00")
    assert result.rows[0].charge_outflow == Decimal("10.00")
    assert result.rows[0].applied_extra == Decimal("90.00")
    assert result.rows[0].actual_cash_outflow == Decimal("600.00")
    assert result.rows[1].actual_cash_outflow == Decimal("420.00")

    with pytest.raises(ValueError, match="cap"):
        simulate(
            _terms(),
            FixedRate(Decimal("0")),
            OverpaymentPlan(monthly_cap=Decimal("509.00")),
            charges=(charge,),
        )


def test_charges_after_contractual_term_are_rejected() -> None:
    charge = Charge(
        Decimal("10.00"),
        ChargeCategory.MANDATORY_CREDIT,
        ChargeCadence.ONCE,
        ChargeFunding.OWN_FUNDS,
        ChargePayee.LENDER,
        due_period=3,
    )

    with pytest.raises(ValueError, match="term"):
        simulate(_terms(), FixedRate(Decimal("0")), charges=(charge,))
