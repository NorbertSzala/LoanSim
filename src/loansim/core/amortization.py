"""Cent-settled monthly amortization with disclosed extra-principal behavior."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, localcontext

from loansim.core.interest import InterestAccrual, monthly_nominal_interest
from loansim.core.models import (
    ZERO,
    Charge,
    ChargeCadence,
    ChargeCategory,
    ChargeFunding,
    ChargePayee,
    InstallmentType,
    LoanTerms,
    OverpaymentPlan,
    OverpaymentResponse,
    financial_precision,
    quantize_cent,
)
from loansim.core.rates import PeriodRate, RatePlan, rate_schedule

CONVENTION_ID = "monthly-nominal-12-half-up-v1"
ESTIMATE_NOTICE = (
    "LoanSim is an estimate for scenario comparison; actual bank schedules may differ."
)


@dataclass(frozen=True, slots=True)
class PaymentRow:
    period: int
    payment_date: date
    rate_detail: PeriodRate
    opening_balance: Decimal
    nominal_annual: Decimal
    effective_annual: Decimal
    rate_source_kind: str
    interest: Decimal
    mandatory_principal: Decimal
    mandatory_payment: Decimal
    requested_extra: Decimal
    applied_extra: Decimal
    charge_outflow: Decimal
    actual_cash_outflow: Decimal
    closing_balance: Decimal


@dataclass(frozen=True, slots=True)
class ChargeEvent:
    period: int
    charge: Charge
    cash_outflow: Decimal


@dataclass(frozen=True, slots=True)
class SimulationResult:
    convention_id: str
    estimate_notice: str
    rows: tuple[PaymentRow, ...]
    charge_events: tuple[ChargeEvent, ...]
    initial_debt: Decimal
    total_interest: Decimal
    total_financing_charges: Decimal
    total_recurring_charges: Decimal
    financing_cost: Decimal
    total_nominal_loan_cost: Decimal
    total_lender_repayments: Decimal
    total_cash_outflow: Decimal
    contractual_months: int
    effective_months: int
    initial_nominal_annual: Decimal
    initial_effective_annual: Decimal
    baseline_total_interest: Decimal | None
    interest_savings: Decimal | None
    acquisition_date_own_funds: Decimal | None
    total_property_acquisition_cost: Decimal | None
    lifetime_buyer_cash_outflow: Decimal | None
    ltv: Decimal | None


def _annuity_payment(balance: Decimal, nominal_annual: Decimal, months: int) -> Decimal:
    if months < 1:
        raise ValueError("annuity requires a remaining period")
    with localcontext() as context:
        context.prec = 50
        period_rate = nominal_annual / Decimal(12)
        if period_rate == 0:
            unrounded = balance / Decimal(months)
        else:
            unrounded = balance * period_rate / (1 - (1 + period_rate) ** (-months))
    return quantize_cent(unrounded)


def _project_payoff_months(
    balance: Decimal,
    payment: Decimal,
    nominal_annual: Decimal,
    future_periods: tuple[PeriodRate, ...],
    accrual: InterestAccrual,
) -> int:
    """Find the earlier target under an unchanged payment and current rate."""
    projected = balance
    for count, future in enumerate(future_periods, start=1):
        interest = accrual(projected, nominal_annual, future.period_start, future.payment_date)
        if payment <= interest:
            raise ValueError("mandatory payment does not cover interest")
        projected -= min(projected, payment - interest)
        if projected == ZERO:
            return count
    return len(future_periods)


def _requested_extra(plan: OverpaymentPlan, period: int, required_cash: Decimal) -> Decimal:
    requested = plan.regular_amount + sum(
        (extra.amount for extra in plan.one_time if extra.period == period), ZERO
    )
    if plan.monthly_cap is None:
        return requested
    if plan.monthly_cap < required_cash:
        raise ValueError("monthly cap is below the mandatory payment")
    cap_extra = plan.monthly_cap - required_cash
    return cap_extra if requested == ZERO else min(requested, cap_extra)


def _charge_due(charge: Charge, period: int) -> bool:
    if charge.cadence is ChargeCadence.ONCE:
        return charge.due_period == period
    return charge.due_period <= period and (
        charge.last_period is None or period <= charge.last_period
    )


def _simulate_rows(
    terms: LoanTerms,
    rates: tuple[PeriodRate, ...],
    plan: OverpaymentPlan,
    initial_debt: Decimal,
    charges: tuple[Charge, ...],
    accrual: InterestAccrual = monthly_nominal_interest,
) -> tuple[PaymentRow, ...]:
    balance = initial_debt
    target_period = terms.term_months
    annuity_payment = (
        _annuity_payment(balance, rates[0].nominal_annual, terms.term_months)
        if terms.installment_type is InstallmentType.ANNUITY
        else ZERO
    )
    declining_principal = (
        quantize_cent(balance / Decimal(terms.term_months))
        if terms.installment_type is InstallmentType.DECLINING
        else ZERO
    )
    rows: list[PaymentRow] = []
    recalculate_next = False
    for period_rate in rates:
        period = period_rate.period
        reset = period > 1 and period_rate.nominal_annual != rates[period - 2].nominal_annual
        if terms.installment_type is InstallmentType.ANNUITY and (reset or recalculate_next):
            annuity_payment = _annuity_payment(
                balance, period_rate.nominal_annual, target_period - period + 1
            )
        recalculate_next = False
        interest = accrual(
            balance,
            period_rate.nominal_annual,
            period_rate.period_start,
            period_rate.payment_date,
        )
        if terms.installment_type is InstallmentType.ANNUITY:
            planned_payment = annuity_payment
        else:
            planned_payment = declining_principal + interest
        if planned_payment <= interest:
            raise ValueError("mandatory payment does not cover interest")
        if period == target_period or period == terms.term_months:
            mandatory = balance + interest
        else:
            mandatory = min(planned_payment, balance + interest)
        mandatory_principal = mandatory - interest
        remaining = balance - mandatory_principal
        charge_outflow = sum(
            (
                charge.amount
                for charge in charges
                if charge.funding is ChargeFunding.OWN_FUNDS and _charge_due(charge, period)
            ),
            ZERO,
        )
        requested_extra = _requested_extra(plan, period, mandatory + charge_outflow)
        applied_extra = min(requested_extra, remaining)
        closing = remaining - applied_extra
        row = PaymentRow(
            period=period,
            payment_date=period_rate.payment_date,
            rate_detail=period_rate,
            opening_balance=balance,
            nominal_annual=period_rate.nominal_annual,
            effective_annual=period_rate.effective_annual,
            rate_source_kind=period_rate.source_kind,
            interest=interest,
            mandatory_principal=mandatory_principal,
            mandatory_payment=mandatory,
            requested_extra=requested_extra,
            applied_extra=applied_extra,
            charge_outflow=charge_outflow,
            actual_cash_outflow=mandatory + applied_extra + charge_outflow,
            closing_balance=closing,
        )
        rows.append(row)
        balance = closing
        if balance == ZERO:
            break
        if applied_extra > ZERO:
            if plan.response is OverpaymentResponse.LOWER_INSTALLMENT:
                target_period = terms.term_months
                if terms.installment_type is InstallmentType.ANNUITY:
                    recalculate_next = True
                else:
                    declining_principal = quantize_cent(balance / Decimal(target_period - period))
            elif terms.installment_type is InstallmentType.ANNUITY:
                target_period = min(
                    target_period,
                    period
                    + _project_payoff_months(
                        balance,
                        annuity_payment,
                        period_rate.nominal_annual,
                        rates[period:target_period],
                        accrual,
                    ),
                )
            else:
                periods_needed = (balance / declining_principal).to_integral_value(
                    rounding="ROUND_CEILING"
                )
                target_period = min(target_period, period + int(periods_needed))
    if balance != ZERO:
        raise ValueError("schedule did not discharge the balance")
    return tuple(rows)


@financial_precision
def simulate(
    terms: LoanTerms,
    rate_plan: RatePlan,
    overpayments: OverpaymentPlan | None = None,
    *,
    charges: tuple[Charge, ...] = (),
) -> SimulationResult:
    """Return a complete, auditable schedule for the approved monthly model."""
    plan = overpayments or OverpaymentPlan()
    if any(extra.period > terms.term_months for extra in plan.one_time):
        raise ValueError("extra-payment period exceeds contractual term")
    if not isinstance(charges, tuple) or not all(isinstance(charge, Charge) for charge in charges):
        raise ValueError("charges must be a tuple of Charge values")
    if any(
        charge.due_period > terms.term_months
        or (charge.last_period is not None and charge.last_period > terms.term_months)
        for charge in charges
    ):
        raise ValueError("charge period exceeds contractual term")
    financed_upfront = sum(
        (charge.amount for charge in charges if charge.funding is ChargeFunding.FINANCED),
        ZERO,
    )
    initial_debt = terms.purchase_loan + financed_upfront
    rates = rate_schedule(rate_plan, terms.term_months, terms.start_date)
    rows = _simulate_rows(terms, rates, plan, initial_debt, charges)
    charge_events = tuple(
        ChargeEvent(
            period,
            charge,
            charge.amount if charge.funding is ChargeFunding.OWN_FUNDS else ZERO,
        )
        for period in (0, *(row.period for row in rows))
        for charge in charges
        if _charge_due(charge, period)
    )
    total_interest = sum((row.interest for row in rows), ZERO)
    upfront_cash = sum((event.cash_outflow for event in charge_events if event.period == 0), ZERO)
    total_outflow = sum((row.actual_cash_outflow for row in rows), upfront_cash)
    total_financing_charges = sum(
        (
            event.charge.amount
            for event in charge_events
            if event.charge.category
            in (ChargeCategory.MANDATORY_CREDIT, ChargeCategory.OPTIONAL_CREDIT)
        ),
        ZERO,
    )
    total_recurring_charges = sum(
        (
            event.charge.amount
            for event in charge_events
            if event.charge.cadence is ChargeCadence.MONTHLY
        ),
        ZERO,
    )
    lender_cash_charges = sum(
        (event.cash_outflow for event in charge_events if event.charge.payee is ChargePayee.LENDER),
        ZERO,
    )
    principal_and_interest_outflow = sum(
        (row.mandatory_payment + row.applied_extra for row in rows), ZERO
    )
    has_extra = any(row.applied_extra > ZERO for row in rows)
    baseline_total_interest = None
    interest_savings = None
    if has_extra:
        baseline = _simulate_rows(terms, rates, OverpaymentPlan(), initial_debt, charges)
        baseline_total_interest = sum((row.interest for row in baseline), ZERO)
        interest_savings = baseline_total_interest - total_interest
    acquisition_date_own_funds = (
        terms.down_payment + upfront_cash if terms.down_payment is not None else None
    )
    acquisition_charges = sum(
        (
            event.charge.amount
            for event in charge_events
            if event.charge.category is ChargeCategory.ACQUISITION
        ),
        ZERO,
    )
    total_property_acquisition_cost = (
        terms.property_price + acquisition_charges if terms.property_price is not None else None
    )
    lifetime_buyer_cash_outflow = (
        terms.down_payment + total_outflow if terms.down_payment is not None else None
    )
    ltv = initial_debt / terms.property_price if terms.property_price is not None else None
    return SimulationResult(
        convention_id=CONVENTION_ID,
        estimate_notice=ESTIMATE_NOTICE,
        rows=rows,
        charge_events=charge_events,
        initial_debt=initial_debt,
        total_interest=total_interest,
        total_financing_charges=total_financing_charges,
        total_recurring_charges=total_recurring_charges,
        financing_cost=total_interest + total_financing_charges,
        total_nominal_loan_cost=total_interest + total_financing_charges,
        total_lender_repayments=principal_and_interest_outflow + lender_cash_charges,
        total_cash_outflow=total_outflow,
        contractual_months=terms.term_months,
        effective_months=len(rows),
        initial_nominal_annual=rates[0].nominal_annual,
        initial_effective_annual=rates[0].effective_annual,
        baseline_total_interest=baseline_total_interest,
        interest_savings=interest_savings,
        acquisition_date_own_funds=acquisition_date_own_funds,
        total_property_acquisition_cost=total_property_acquisition_cost,
        lifetime_buyer_cash_outflow=lifetime_buyer_cash_outflow,
        ltv=ltv,
    )
