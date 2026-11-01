"""Independent payment references and strategy behavior for Phase 1."""

from datetime import date
from decimal import Decimal

import pytest

from loansim.core.amortization import simulate
from loansim.core.interest import monthly_nominal_interest
from loansim.core.models import (
    ExtraPayment,
    InstallmentType,
    LoanTerms,
    OverpaymentPlan,
    OverpaymentResponse,
)
from loansim.core.rates import FixedRate, PeriodicallyFixedRate, RateObservation, VariableRate


def _terms(amount: str, months: int, kind: InstallmentType) -> LoanTerms:
    return LoanTerms(Decimal(amount), months, date(2026, 1, 1), kind)


def test_monthly_accrual_ignores_calendar_day_count() -> None:
    january = monthly_nominal_interest(
        Decimal("1000.00"), Decimal("0.12"), date(2026, 1, 31), date(2026, 2, 28)
    )
    march = monthly_nominal_interest(
        Decimal("1000.00"), Decimal("0.12"), date(2026, 3, 31), date(2026, 4, 30)
    )

    assert january == march == Decimal("10.00")


def test_two_period_annuity_matches_independent_cent_schedule() -> None:
    result = simulate(_terms("1000.00", 2, InstallmentType.ANNUITY), FixedRate(Decimal("0.12")))

    assert [
        (r.interest, r.mandatory_principal, r.actual_cash_outflow, r.closing_balance)
        for r in result.rows
    ] == [
        (Decimal("10.00"), Decimal("497.51"), Decimal("507.51"), Decimal("502.49")),
        (Decimal("5.02"), Decimal("502.49"), Decimal("507.51"), Decimal("0.00")),
    ]
    assert result.total_interest == Decimal("15.02")
    assert result.total_lender_repayments == Decimal("1015.02")
    assert result.effective_months == 2
    assert result.convention_id == "monthly-nominal-12-half-up-v1"
    assert "estimate" in result.estimate_notice.lower()
    assert "bank" in result.estimate_notice.lower()
    assert result.total_nominal_loan_cost == Decimal("15.02")
    assert not hasattr(result, "rrso")


def test_two_period_declining_schedule_matches_independent_reference() -> None:
    result = simulate(_terms("1000.00", 2, InstallmentType.DECLINING), FixedRate(Decimal("0.12")))

    assert [r.actual_cash_outflow for r in result.rows] == [Decimal("510.00"), Decimal("505.00")]
    assert [r.mandatory_principal for r in result.rows] == [Decimal("500.00")] * 2
    assert result.total_interest == Decimal("15.00")


def test_openstax_first_row_is_an_independent_annuity_reference() -> None:
    result = simulate(_terms("32000.00", 36, InstallmentType.ANNUITY), FixedRate(Decimal("0.06")))

    assert result.rows[0].mandatory_payment == Decimal("973.50")
    assert result.rows[0].interest == Decimal("160.00")
    assert result.rows[0].mandatory_principal == Decimal("813.50")
    assert result.rows[0].closing_balance == Decimal("31186.50")


def test_zero_interest_clears_rounding_residual_in_final_payment() -> None:
    result = simulate(_terms("1000.00", 3, InstallmentType.ANNUITY), FixedRate(Decimal("0")))

    assert [r.mandatory_payment for r in result.rows] == [
        Decimal("333.33"),
        Decimal("333.33"),
        Decimal("333.34"),
    ]
    assert result.rows[-1].closing_balance == Decimal("0.00")


def test_period_interest_rounds_half_up_once() -> None:
    result = simulate(_terms("100.50", 1, InstallmentType.ANNUITY), FixedRate(Decimal("0.12")))

    assert result.rows[0].interest == Decimal("1.01")
    assert result.rows[0].actual_cash_outflow == Decimal("101.51")


def test_non_amortizing_rounded_installment_is_rejected() -> None:
    with pytest.raises(ValueError, match="interest"):
        simulate(_terms("0.01", 120, InstallmentType.ANNUITY), FixedRate(Decimal("0.12")))


def test_one_time_extra_payment_shortens_term_and_caps_final_cash() -> None:
    plan = OverpaymentPlan(
        response=OverpaymentResponse.SHORTEN_TERM,
        one_time=(ExtraPayment(1, Decimal("100.00")),),
    )
    result = simulate(
        _terms("1000.00", 2, InstallmentType.ANNUITY),
        FixedRate(Decimal("0.12")),
        plan,
    )

    assert result.rows[0].applied_extra == Decimal("100.00")
    assert result.rows[0].closing_balance == Decimal("402.49")
    assert result.rows[1].interest == Decimal("4.02")
    assert result.rows[1].actual_cash_outflow == Decimal("406.51")
    assert result.total_interest == Decimal("14.02")
    assert result.interest_savings == Decimal("1.00")


def test_lower_installment_and_shorten_term_have_distinct_mandatory_obligations() -> None:
    terms = _terms("1000.00", 4, InstallmentType.ANNUITY)
    extra = (ExtraPayment(1, Decimal("100.00")),)
    shortened = simulate(
        terms,
        FixedRate(Decimal("0.12")),
        OverpaymentPlan(OverpaymentResponse.SHORTEN_TERM, one_time=extra),
    )
    lowered = simulate(
        terms,
        FixedRate(Decimal("0.12")),
        OverpaymentPlan(OverpaymentResponse.LOWER_INSTALLMENT, one_time=extra),
    )

    assert shortened.rows[1].mandatory_payment > lowered.rows[1].mandatory_payment
    assert shortened.total_interest <= lowered.total_interest


def test_rate_reset_recalculates_annuity_for_remaining_target() -> None:
    rate = PeriodicallyFixedRate(Decimal("0.00"), 1, FixedRate(Decimal("0.12")))
    result = simulate(_terms("1200.00", 3, InstallmentType.ANNUITY), rate)

    assert result.rows[0].mandatory_payment == Decimal("400.00")
    assert result.rows[1].mandatory_payment == Decimal("406.01")
    assert result.rows[1].interest == Decimal("8.00")


def test_payment_row_preserves_applied_rate_provenance() -> None:
    rate = VariableRate(
        "POLSTR 1M compounded",
        Decimal("0.02"),
        (
            RateObservation(
                1,
                Decimal("0.04"),
                "historical",
                "example series",
                date(2025, 12, 31),
                date(2025, 12, 30),
            ),
        ),
        date(2026, 1, 1),
    )
    result = simulate(_terms("1000.00", 2, InstallmentType.ANNUITY), rate)

    assert result.rows[0].rate_detail.index_name == "POLSTR 1M compounded"
    assert result.rows[0].rate_detail.margin == Decimal("0.02")
    assert result.rows[0].rate_detail.published_on == date(2025, 12, 31)
    assert result.rows[1].rate_detail.source_kind == "constant_future"


def test_combined_payment_cap_below_mandatory_is_rejected() -> None:
    plan = OverpaymentPlan(OverpaymentResponse.SHORTEN_TERM, monthly_cap=Decimal("400.00"))

    with pytest.raises(ValueError, match="cap"):
        simulate(_terms("1000.00", 2, InstallmentType.ANNUITY), FixedRate(Decimal("0.12")), plan)


def test_excess_extra_request_is_capped_to_remaining_principal() -> None:
    plan = OverpaymentPlan(
        OverpaymentResponse.SHORTEN_TERM,
        one_time=(ExtraPayment(1, Decimal("2000.00")),),
    )
    result = simulate(_terms("1000.00", 2, InstallmentType.ANNUITY), FixedRate(Decimal("0")), plan)

    assert result.effective_months == 1
    assert result.rows[0].requested_extra == Decimal("2000.00")
    assert result.rows[0].applied_extra == Decimal("500.00")
    assert result.rows[0].actual_cash_outflow == Decimal("1000.00")


def test_declining_extra_payment_keeps_or_lowers_regular_principal() -> None:
    terms = _terms("1000.00", 4, InstallmentType.DECLINING)
    extra = (ExtraPayment(1, Decimal("100.00")),)
    shortened = simulate(
        terms,
        FixedRate(Decimal("0")),
        OverpaymentPlan(OverpaymentResponse.SHORTEN_TERM, one_time=extra),
    )
    lowered = simulate(
        terms,
        FixedRate(Decimal("0")),
        OverpaymentPlan(OverpaymentResponse.LOWER_INSTALLMENT, one_time=extra),
    )

    assert shortened.rows[1].mandatory_principal == Decimal("250.00")
    assert lowered.rows[1].mandatory_principal == Decimal("216.67")
