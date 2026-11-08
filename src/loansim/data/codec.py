"""Explicit JSON codec for validated core inputs and complete result snapshots."""

import json
from dataclasses import dataclass, fields, is_dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any

from loansim.core.amortization import ChargeEvent, PaymentRow, SimulationResult
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
    OverpaymentResponse,
)
from loansim.core.rates import (
    FixedRate,
    PeriodicallyFixedRate,
    PeriodRate,
    RateObservation,
    RatePlan,
    VariableRate,
)

FORMAT_VERSION = 1
_TYPES = {
    type_.__name__: type_
    for type_ in (
        Charge,
        ExtraPayment,
        LoanTerms,
        OverpaymentPlan,
        FixedRate,
        RateObservation,
        VariableRate,
        PeriodicallyFixedRate,
        PeriodRate,
        PaymentRow,
        ChargeEvent,
        SimulationResult,
    )
}
_ENUMS = {
    type_.__name__: type_
    for type_ in (
        InstallmentType,
        OverpaymentResponse,
        ChargeCategory,
        ChargeCadence,
        ChargeFunding,
        ChargePayee,
    )
}


@dataclass(frozen=True, slots=True)
class ScenarioSnapshot:
    """The entered state and exact engine result at the time of saving."""

    original_inputs: dict[str, object]
    derived_inputs: dict[str, object]
    terms: LoanTerms
    rate_plan: RatePlan
    overpayments: OverpaymentPlan
    charges: tuple[Charge, ...]
    result: SimulationResult

    def __post_init__(self) -> None:
        if (
            not isinstance(self.terms, LoanTerms)
            or not isinstance(self.rate_plan, (FixedRate, VariableRate, PeriodicallyFixedRate))
            or not isinstance(self.overpayments, OverpaymentPlan)
        ):
            raise ValueError("scenario inputs are invalid")
        if (
            not isinstance(self.charges, tuple)
            or not all(isinstance(charge, Charge) for charge in self.charges)
            or not isinstance(self.result, SimulationResult)
        ):
            raise ValueError("scenario charges or result are invalid")
        if not isinstance(self.original_inputs, dict) or not isinstance(self.derived_inputs, dict):
            raise ValueError("scenario input provenance is invalid")
        if not all(isinstance(key, str) for key in self.original_inputs | self.derived_inputs):
            raise ValueError("scenario input keys must be strings")
        if (
            not self.result.convention_id
            or self.result.contractual_months != self.terms.term_months
        ):
            raise ValueError("scenario result does not match its inputs")


def _encode(value: object) -> object:
    if isinstance(value, Enum):
        return {"__enum__": type(value).__name__, "value": value.value}
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("non-finite Decimal is unsupported")
        return {"__decimal__": str(value)}
    if isinstance(value, date):
        return {"__date__": value.isoformat()}
    if is_dataclass(value) and not isinstance(value, type):
        name = type(value).__name__
        if name not in _TYPES or type(value) is not _TYPES[name]:
            raise ValueError(f"unsupported snapshot type: {name}")
        return {
            "__type__": name,
            "fields": {field.name: _encode(getattr(value, field.name)) for field in fields(value)},
        }
    if isinstance(value, tuple):
        return {"__tuple__": [_encode(item) for item in value]}
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ValueError("snapshot object keys must be strings")
        return {"__dict__": {key: _encode(item) for key, item in value.items()}}
    if value is None or type(value) in (str, int, bool):
        return value
    raise ValueError(f"unsupported snapshot value: {type(value).__name__}")


def _decode(value: Any) -> Any:
    if isinstance(value, list):
        return [_decode(item) for item in value]
    if not isinstance(value, dict):
        if value is None or type(value) in (str, int, bool):
            return value
        raise ValueError("unsupported JSON value")
    if len(value) == 1 and "__decimal__" in value:
        decimal_value = Decimal(value["__decimal__"])
        if not decimal_value.is_finite():
            raise ValueError("non-finite Decimal is unsupported")
        return decimal_value
    if len(value) == 1 and "__date__" in value:
        return date.fromisoformat(value["__date__"])
    if len(value) == 1 and "__tuple__" in value:
        return tuple(_decode(item) for item in value["__tuple__"])
    if len(value) == 1 and "__dict__" in value:
        return {key: _decode(item) for key, item in value["__dict__"].items()}
    if set(value) == {"__enum__", "value"}:
        enum_type = _ENUMS.get(value["__enum__"])
        if enum_type is None:
            raise ValueError("unknown snapshot enum")
        return enum_type(value["value"])
    if set(value) == {"__type__", "fields"}:
        data_type = _TYPES.get(value["__type__"])
        if data_type is None:
            raise ValueError("unsupported snapshot type")
        decoded_fields = {key: _decode(item) for key, item in value["fields"].items()}
        try:
            return data_type(**decoded_fields)
        except (TypeError, ValueError) as error:
            raise ValueError("invalid snapshot object") from error
    raise ValueError("unsupported snapshot object")


def encode_snapshot(snapshot: ScenarioSnapshot) -> str:
    """Store a snapshot without binary floats or executable Python payloads."""
    if not isinstance(snapshot, ScenarioSnapshot):
        raise ValueError("snapshot is invalid")
    payload = {
        "format_version": FORMAT_VERSION,
        "snapshot": {
            field.name: _encode(getattr(snapshot, field.name)) for field in fields(snapshot)
        },
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def decode_snapshot(payload: str) -> ScenarioSnapshot:
    """Reject unknown formats and reconstruct only allowlisted core types."""
    try:
        document = json.loads(payload)
        if not isinstance(document, dict) or document.get("format_version") != FORMAT_VERSION:
            raise ValueError("unsupported snapshot format version")
        data = document["snapshot"]
        if not isinstance(data, dict):
            raise ValueError("invalid snapshot document")
        return ScenarioSnapshot(**{key: _decode(item) for key, item in data.items()})
    except (KeyError, TypeError, json.JSONDecodeError) as error:
        raise ValueError("invalid snapshot document") from error
