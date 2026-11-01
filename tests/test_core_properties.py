"""Financial invariants across many valid monthly loan inputs."""

from datetime import date
from decimal import Decimal, localcontext

from hypothesis import given, settings
from hypothesis import strategies as st

from loansim.core.amortization import simulate
from loansim.core.models import (
    ExtraPayment,
    InstallmentType,
    LoanTerms,
    OverpaymentPlan,
    OverpaymentResponse,
)
from loansim.core.rates import FixedRate

CENT = Decimal("0.01")


@settings(max_examples=80, deadline=None)
@given(
    principal_cents=st.integers(min_value=10_000, max_value=10_000_000),
    months=st.integers(min_value=1, max_value=120),
    rate_basis_points=st.integers(min_value=0, max_value=2000),
    kind=st.sampled_from(list(InstallmentType)),
)
def test_schedule_reconciles_every_cent_and_disposes_of_principal(
    principal_cents: int, months: int, rate_basis_points: int, kind: InstallmentType
) -> None:
    principal = Decimal(principal_cents) / 100
    annual_rate = Decimal(rate_basis_points) / 10_000
    result = simulate(LoanTerms(principal, months, date(2026, 1, 31), kind), FixedRate(annual_rate))

    assert result.rows[-1].closing_balance == Decimal("0.00")
    assert len(result.rows) == months
    assert (
        sum((row.mandatory_principal + row.applied_extra for row in result.rows), Decimal(0))
        == principal
    )
    assert result.total_interest == sum((row.interest for row in result.rows), Decimal(0))
    for row in result.rows:
        assert (
            row.opening_balance - row.mandatory_principal - row.applied_extra == row.closing_balance
        )
        assert row.mandatory_payment == row.interest + row.mandatory_principal
        assert (
            row.actual_cash_outflow
            == row.mandatory_payment + row.applied_extra + row.charge_outflow
        )
        assert row.closing_balance >= 0
        assert all(
            amount == amount.quantize(CENT)
            for amount in (
                row.interest,
                row.mandatory_principal,
                row.mandatory_payment,
                row.actual_cash_outflow,
                row.closing_balance,
            )
        )


@settings(max_examples=50, deadline=None)
@given(
    principal_cents=st.integers(min_value=100_000, max_value=10_000_000),
    months=st.integers(min_value=2, max_value=60),
    rate_basis_points=st.integers(min_value=0, max_value=2000),
    extra_cents=st.integers(min_value=1, max_value=50_000),
)
def test_more_principal_paid_early_does_not_increase_interest(
    principal_cents: int, months: int, rate_basis_points: int, extra_cents: int
) -> None:
    terms = LoanTerms(
        Decimal(principal_cents) / 100,
        months,
        date(2026, 1, 1),
        InstallmentType.ANNUITY,
    )
    rate = FixedRate(Decimal(rate_basis_points) / 10_000)
    base = simulate(terms, rate)
    early = simulate(
        terms,
        rate,
        OverpaymentPlan(
            OverpaymentResponse.SHORTEN_TERM,
            one_time=(ExtraPayment(1, Decimal(extra_cents) / 100),),
        ),
    )

    assert early.total_interest <= base.total_interest


def test_identical_actual_cash_flows_give_identical_balances_and_interest() -> None:
    terms = LoanTerms(Decimal("1000.00"), 4, date(2026, 1, 1), InstallmentType.ANNUITY)
    rate = FixedRate(Decimal("0.12"))
    shorten = simulate(
        terms,
        rate,
        OverpaymentPlan(
            OverpaymentResponse.SHORTEN_TERM,
            one_time=(ExtraPayment(1, Decimal("100.00")),),
        ),
    )
    lower = simulate(
        terms,
        rate,
        OverpaymentPlan(
            OverpaymentResponse.LOWER_INSTALLMENT,
            one_time=(
                ExtraPayment(1, Decimal("100.00")),
                ExtraPayment(2, Decimal("34.00")),
                ExtraPayment(3, Decimal("51.26")),
            ),
        ),
    )

    assert [row.actual_cash_outflow for row in shorten.rows] == [
        row.actual_cash_outflow for row in lower.rows
    ]
    assert [row.closing_balance for row in shorten.rows] == [
        row.closing_balance for row in lower.rows
    ]
    assert shorten.total_interest == lower.total_interest
    assert [row.mandatory_payment for row in shorten.rows] != [
        row.mandatory_payment for row in lower.rows
    ]


def test_caller_decimal_context_does_not_change_financial_results() -> None:
    terms = LoanTerms(Decimal("32000.00"), 36, date(2026, 1, 1), InstallmentType.ANNUITY)
    rate = FixedRate(Decimal("0.06"))
    reference = simulate(terms, rate)

    with localcontext() as context:
        context.prec = 8
        altered = simulate(terms, rate)

    assert altered.rows == reference.rows
    assert altered.total_interest == reference.total_interest
    assert altered.initial_effective_annual == reference.initial_effective_annual
