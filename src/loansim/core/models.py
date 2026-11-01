"""Immutable inputs and monetary validation for the Phase 1 engine."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal, localcontext
from enum import StrEnum
from functools import wraps
from typing import ParamSpec, TypeVar

CENT = Decimal("0.01")
ZERO = Decimal("0.00")
P = ParamSpec("P")
T = TypeVar("T")


def financial_precision(function: Callable[P, T]) -> Callable[P, T]:
    """Keep intermediate arithmetic independent of the caller's Decimal context."""

    @wraps(function)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        with localcontext() as context:
            context.prec = 50
            return function(*args, **kwargs)

    return wrapped


def require_decimal(value: Decimal, name: str) -> Decimal:
    """Reject binary floats and non-finite values at the calculation boundary."""
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(f"{name} must be a finite Decimal")
    return value


def quantize_cent(value: Decimal) -> Decimal:
    """Round a calculated settlement amount to PLN cents."""
    require_decimal(value, "value")
    with localcontext() as context:
        context.prec = max(50, len(value.as_tuple().digits) + 4)
        return value.quantize(CENT, rounding=ROUND_HALF_UP)


def require_money(value: Decimal, name: str, *, positive: bool = False) -> Decimal:
    """Validate an entered PLN amount without silently rounding it."""
    require_decimal(value, name)
    if value != quantize_cent(value):
        raise ValueError(f"{name} must have at most two decimal places")
    if (positive and value <= ZERO) or (not positive and value < ZERO):
        raise ValueError(f"{name} must be {'positive' if positive else 'nonnegative'}")
    return value


class InstallmentType(StrEnum):
    """Supported mandatory repayment profiles."""

    ANNUITY = "annuity"
    DECLINING = "declining"


class OverpaymentResponse(StrEnum):
    """Effect of extra principal on future mandatory payments."""

    SHORTEN_TERM = "shorten_term"
    LOWER_INSTALLMENT = "lower_installment"


class ChargeCategory(StrEnum):
    MANDATORY_CREDIT = "mandatory_credit"
    OPTIONAL_CREDIT = "optional_credit"
    ACQUISITION = "acquisition"


class ChargeCadence(StrEnum):
    ONCE = "once"
    MONTHLY = "monthly"


class ChargeFunding(StrEnum):
    OWN_FUNDS = "own_funds"
    FINANCED = "financed"


class ChargePayee(StrEnum):
    LENDER = "lender"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Charge:
    amount: Decimal
    category: ChargeCategory
    cadence: ChargeCadence
    funding: ChargeFunding
    payee: ChargePayee
    due_period: int = 0
    last_period: int | None = None
    name: str = ""

    def __post_init__(self) -> None:
        require_money(self.amount, "charge amount", positive=True)
        if not all(
            (
                isinstance(self.category, ChargeCategory),
                isinstance(self.cadence, ChargeCadence),
                isinstance(self.funding, ChargeFunding),
                isinstance(self.payee, ChargePayee),
            )
        ):
            raise ValueError("charge classification is invalid")
        if type(self.due_period) is not int or self.due_period < 0:
            raise ValueError("charge due_period is invalid")
        if self.cadence is ChargeCadence.ONCE and self.last_period is not None:
            raise ValueError("one-time charge has no last_period")
        if self.cadence is ChargeCadence.MONTHLY:
            if self.funding is ChargeFunding.FINANCED:
                raise ValueError(
                    "Recurring charges in Phase 1 must be paid from own funds; "
                    "financing them with the loan is unsupported"
                )
            if self.due_period < 1:
                raise ValueError("monthly charge begins no earlier than period 1")
            if self.last_period is not None and (
                type(self.last_period) is not int or self.last_period < self.due_period
            ):
                raise ValueError("monthly charge last_period is invalid")
        if self.funding is ChargeFunding.FINANCED and self.due_period != 0:
            raise ValueError("financed one-time charge must be funded at origination")


@dataclass(frozen=True, slots=True)
class ExtraPayment:
    period: int
    amount: Decimal

    def __post_init__(self) -> None:
        if type(self.period) is not int or self.period < 1:
            raise ValueError("extra-payment period must be positive")
        require_money(self.amount, "extra-payment amount", positive=True)


@dataclass(frozen=True, slots=True)
class OverpaymentPlan:
    response: OverpaymentResponse = OverpaymentResponse.SHORTEN_TERM
    regular_amount: Decimal = ZERO
    one_time: tuple[ExtraPayment, ...] = ()
    monthly_cap: Decimal | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.response, OverpaymentResponse):
            raise ValueError("overpayment response is unsupported")
        require_money(self.regular_amount, "regular_amount")
        if not isinstance(self.one_time, tuple) or not all(
            isinstance(extra, ExtraPayment) for extra in self.one_time
        ):
            raise ValueError("one_time must contain ExtraPayment values")
        if self.monthly_cap is not None:
            require_money(self.monthly_cap, "monthly_cap", positive=True)


@dataclass(frozen=True, slots=True)
class LoanTerms:
    """Purchase financing before separately modeled financed charges."""

    purchase_loan: Decimal
    term_months: int
    start_date: date
    installment_type: InstallmentType
    currency: str = "PLN"
    property_price: Decimal | None = None
    down_payment: Decimal | None = None

    def __post_init__(self) -> None:
        require_money(self.purchase_loan, "purchase_loan", positive=True)
        if type(self.term_months) is not int or self.term_months < 1:
            raise ValueError("term_months must be a positive integer")
        if type(self.start_date) is not date:
            raise ValueError("start_date must be a date")
        if not isinstance(self.installment_type, InstallmentType):
            raise ValueError("installment_type is unsupported")
        if self.currency != "PLN":
            raise ValueError("Phase 1 supports PLN only")
        if (self.property_price is None) != (self.down_payment is None):
            raise ValueError("property_price and down_payment must be supplied together")
        if self.property_price is not None and self.down_payment is not None:
            require_money(self.property_price, "property_price", positive=True)
            require_money(self.down_payment, "down_payment")
            if self.down_payment > self.property_price:
                raise ValueError("down_payment cannot exceed property_price")
            if self.property_price - self.down_payment != self.purchase_loan:
                raise ValueError("property_price, down_payment, and purchase_loan conflict")
