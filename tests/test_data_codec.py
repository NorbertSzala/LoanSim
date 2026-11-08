"""Round-trip tests for reproducible scenario snapshots."""

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
    ExtraPayment,
    InstallmentType,
    LoanTerms,
    OverpaymentPlan,
)
from loansim.core.rates import FixedRate, RateObservation, VariableRate
from loansim.data.codec import ScenarioSnapshot, decode_snapshot, encode_snapshot


def sample_snapshot() -> ScenarioSnapshot:
    terms = LoanTerms(
        Decimal("1000.00"),
        2,
        date(2026, 1, 31),
        InstallmentType.ANNUITY,
        property_price=Decimal("1250.00"),
        down_payment=Decimal("250.00"),
    )
    rate = FixedRate(Decimal("0.12"), "manual scenario")
    plan = OverpaymentPlan()
    return ScenarioSnapshot(
        original_inputs={"price": "1250.00", "down_payment": "250.00"},
        derived_inputs={"purchase_loan": {"value": "1000.00", "formula": "price - down_payment"}},
        terms=terms,
        rate_plan=rate,
        overpayments=plan,
        charges=(),
        result=simulate(terms, rate, plan),
    )


def test_snapshot_round_trip_keeps_exact_money_dates_and_inputs() -> None:
    original = sample_snapshot()
    restored = decode_snapshot(encode_snapshot(original))
    assert restored == original
    assert restored.result.rows[0].payment_date == date(2026, 2, 28)
    assert restored.result.total_interest == Decimal("15.02")


def test_snapshot_rejects_unknown_type_tag() -> None:
    payload = encode_snapshot(sample_snapshot()).replace('"LoanTerms"', '"UntrustedClass"', 1)
    with pytest.raises(ValueError, match="unsupported|unknown"):
        decode_snapshot(payload)


def test_snapshot_rejects_unknown_format_version() -> None:
    payload = encode_snapshot(sample_snapshot()).replace(
        '"format_version":1', '"format_version":999'
    )
    with pytest.raises(ValueError, match="version"):
        decode_snapshot(payload)


def test_variable_rate_charge_and_overpayment_survive_round_trip() -> None:
    terms = LoanTerms(Decimal("1000.00"), 2, date(2026, 1, 1), InstallmentType.ANNUITY)
    rate = VariableRate(
        "manual index",
        Decimal("0.02"),
        (RateObservation(1, Decimal("0.05"), "hypothetical", "owner assumption"),),
        date(2025, 12, 31),
    )
    plan = OverpaymentPlan(one_time=(ExtraPayment(1, Decimal("100.00")),))
    charge = Charge(
        Decimal("10.00"),
        ChargeCategory.MANDATORY_CREDIT,
        ChargeCadence.MONTHLY,
        ChargeFunding.OWN_FUNDS,
        ChargePayee.LENDER,
        due_period=1,
    )
    original = ScenarioSnapshot(
        {"rate_type": "variable"},
        {"ltv": {"reason": "missing property price"}},
        terms,
        rate,
        plan,
        (charge,),
        simulate(terms, rate, plan, charges=(charge,)),
    )
    restored = decode_snapshot(encode_snapshot(original))
    assert restored == original
    assert restored.result.rows[1].rate_source_kind == "constant_future"
