"""Bounded, provenance-preserving derivation of independent inputs."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from loansim.core.amortization import _annuity_payment
from loansim.core.models import (
    financial_precision,
    quantize_cent,
    require_decimal,
    require_money,
)

Origin = Literal["entered", "derived", "missing"]
MISSING_REASON = "insufficient independent inputs"


@dataclass(frozen=True, slots=True)
class DerivedValue:
    """A supplied, calculated, or unavailable value with its explanation."""

    value: Decimal | None
    origin: Origin
    formula: str | None = None
    inputs: tuple[str, ...] = ()
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class PropertyDerivation:
    price: DerivedValue
    down_payment: DerivedValue
    purchase_loan: DerivedValue
    down_fraction: DerivedValue
    initial_debt: DerivedValue
    ltv: DerivedValue


@dataclass(frozen=True, slots=True)
class RateDerivation:
    nominal_annual: DerivedValue
    index_annual: DerivedValue
    margin: DerivedValue


@dataclass(frozen=True, slots=True)
class DerivedTerm:
    months: int | None
    origin: Origin
    reason: str | None = None


def _entered(value: Decimal | None) -> DerivedValue:
    return DerivedValue(
        value,
        "entered" if value is not None else "missing",
        reason=None if value is not None else MISSING_REASON,
    )


def _set(
    values: dict[str, DerivedValue],
    name: str,
    candidate: Decimal,
    formula: str,
    inputs: tuple[str, ...],
    *,
    money: bool = False,
) -> bool:
    if not candidate.is_finite():
        raise ValueError(f"{name} is not finite")
    if money and candidate != quantize_cent(candidate):
        from_ratio = any(field in ("down_fraction", "ltv") for field in inputs)
        rounded = quantize_cent(candidate)
        tolerance = (abs(rounded) + 1) * Decimal("1e-40")
        if not from_ratio or abs(candidate - rounded) > tolerance:
            raise ValueError(f"{name} is not uniquely representable to a cent")
        candidate = rounded
    existing = values[name]
    if existing.value is not None:
        if existing.value != candidate:
            raise ValueError(f"{name} conflict between supplied and derived values")
        return False
    values[name] = DerivedValue(candidate, "derived", formula, inputs)
    return True


@financial_precision
def derive_property(
    *,
    price: Decimal | None = None,
    down_payment: Decimal | None = None,
    purchase_loan: Decimal | None = None,
    down_fraction: Decimal | None = None,
    ltv: Decimal | None = None,
    financed_charges: Decimal = Decimal("0.00"),
) -> PropertyDerivation:
    """Solve exact cent and ratio equations without changing entered values."""
    for name, value in (
        ("price", price),
        ("down_payment", down_payment),
        ("purchase_loan", purchase_loan),
    ):
        if value is not None:
            require_money(value, name, positive=name == "price")
    require_money(financed_charges, "financed_charges")
    for name, value in (("down_fraction", down_fraction), ("ltv", ltv)):
        if value is not None:
            require_decimal(value, name)
            if value < 0 or (name == "down_fraction" and value > 1):
                raise ValueError(f"{name} is outside the supported range")
    values = {
        "price": _entered(price),
        "down_payment": _entered(down_payment),
        "purchase_loan": _entered(purchase_loan),
        "down_fraction": _entered(down_fraction),
        "ltv": _entered(ltv),
        "initial_debt": _entered(None),
    }

    def val(name: str) -> Decimal | None:
        return values[name].value

    # Every pass derives at least one field or stops; there are only six fields.
    for _ in range(7):
        changed = False
        p, d, loan, frac, ratio = (
            val("price"),
            val("down_payment"),
            val("purchase_loan"),
            val("down_fraction"),
            val("ltv"),
        )
        if p is not None and d is not None:
            changed |= _set(
                values,
                "purchase_loan",
                p - d,
                "price - down_payment",
                ("price", "down_payment"),
                money=True,
            )
        if p is not None and loan is not None:
            changed |= _set(
                values,
                "down_payment",
                p - loan,
                "price - purchase_loan",
                ("price", "purchase_loan"),
                money=True,
            )
        if d is not None and loan is not None:
            changed |= _set(
                values,
                "price",
                d + loan,
                "down_payment + purchase_loan",
                ("down_payment", "purchase_loan"),
                money=True,
            )
        if p is not None and frac is not None:
            changed |= _set(
                values,
                "down_payment",
                p * frac,
                "price * down_fraction",
                ("price", "down_fraction"),
                money=True,
            )
        if p is not None and d is not None and p > 0:
            changed |= _set(
                values, "down_fraction", d / p, "down_payment / price", ("down_payment", "price")
            )
        if d is not None and frac is not None and frac > 0:
            changed |= _set(
                values,
                "price",
                d / frac,
                "down_payment / down_fraction",
                ("down_payment", "down_fraction"),
                money=True,
            )
        if loan is not None and frac is not None and frac < 1:
            changed |= _set(
                values,
                "price",
                loan / (1 - frac),
                "purchase_loan / (1 - down_fraction)",
                ("purchase_loan", "down_fraction"),
                money=True,
            )
        if d is not None and ratio is not None:
            denominator = Decimal(1) - ratio
            numerator = d - financed_charges
            if denominator == 0 and numerator != 0:
                raise ValueError("down_payment and ltv conflict")
            if denominator != 0:
                changed |= _set(
                    values,
                    "price",
                    numerator / denominator,
                    "(down_payment - financed_charges) / (1 - ltv)",
                    ("down_payment", "ltv", "financed_charges"),
                    money=True,
                )
        if frac is not None and ratio is not None:
            denominator = ratio - Decimal(1) + frac
            if financed_charges == 0:
                entered_ratios = (
                    values["down_fraction"].origin == "entered"
                    and values["ltv"].origin == "entered"
                )
                tolerance = Decimal(0) if entered_ratios else Decimal("1e-40")
                if abs(denominator) > tolerance:
                    raise ValueError("down_fraction and ltv conflict")
            elif denominator == 0:
                raise ValueError("down_fraction and ltv conflict")
            else:
                changed |= _set(
                    values,
                    "price",
                    financed_charges / denominator,
                    "financed_charges / (ltv - 1 + down_fraction)",
                    ("financed_charges", "ltv", "down_fraction"),
                    money=True,
                )
        if loan is not None:
            changed |= _set(
                values,
                "initial_debt",
                loan + financed_charges,
                "purchase_loan + financed_charges",
                ("purchase_loan", "financed_charges"),
                money=True,
            )
        if p is not None and ratio is not None:
            changed |= _set(
                values, "initial_debt", p * ratio, "price * ltv", ("price", "ltv"), money=True
            )
        debt = val("initial_debt")
        if p is not None and debt is not None and p > 0:
            changed |= _set(
                values, "ltv", debt / p, "initial_debt / price", ("initial_debt", "price")
            )
        if debt is not None and ratio is not None and ratio > 0:
            changed |= _set(
                values,
                "price",
                debt / ratio,
                "initial_debt / ltv",
                ("initial_debt", "ltv"),
                money=True,
            )
        if debt is not None:
            changed |= _set(
                values,
                "purchase_loan",
                debt - financed_charges,
                "initial_debt - financed_charges",
                ("initial_debt", "financed_charges"),
                money=True,
            )
        if not changed:
            break

    final_price = val("price")
    final_down_payment = val("down_payment")
    final_purchase_loan = val("purchase_loan")
    if final_price is not None and final_price <= 0:
        raise ValueError("price must be positive")
    if final_down_payment is not None and final_down_payment < 0:
        raise ValueError("down_payment must be nonnegative")
    if final_purchase_loan is not None and final_purchase_loan < 0:
        raise ValueError("purchase_loan must be nonnegative")
    return PropertyDerivation(
        values["price"],
        values["down_payment"],
        values["purchase_loan"],
        values["down_fraction"],
        values["initial_debt"],
        values["ltv"],
    )


@financial_precision
def derive_rate_components(
    *,
    nominal_annual: Decimal | None = None,
    index_annual: Decimal | None = None,
    margin: Decimal | None = None,
) -> RateDerivation:
    """Solve `nominal_annual = index_annual + margin` if two are supplied."""
    for name, value in (
        ("nominal_annual", nominal_annual),
        ("index_annual", index_annual),
        ("margin", margin),
    ):
        if value is not None:
            require_decimal(value, name)
    values = {
        "nominal_annual": _entered(nominal_annual),
        "index_annual": _entered(index_annual),
        "margin": _entered(margin),
    }
    if index_annual is not None and margin is not None:
        _set(
            values,
            "nominal_annual",
            index_annual + margin,
            "index_annual + margin",
            ("index_annual", "margin"),
        )
    if nominal_annual is not None and index_annual is not None:
        _set(
            values,
            "margin",
            nominal_annual - index_annual,
            "nominal_annual - index_annual",
            ("nominal_annual", "index_annual"),
        )
    if nominal_annual is not None and margin is not None:
        _set(
            values,
            "index_annual",
            nominal_annual - margin,
            "nominal_annual - margin",
            ("nominal_annual", "margin"),
        )
    total = values["nominal_annual"].value
    if total is not None and total < 0:
        raise ValueError("total nominal annual rate cannot be negative")
    return RateDerivation(values["nominal_annual"], values["index_annual"], values["margin"])


def derive_annuity_installment(
    initial_debt: Decimal, nominal_annual: Decimal, term_months: int
) -> DerivedValue:
    """Derive a rounded fixed-rate annuity obligation with explicit provenance."""
    require_money(initial_debt, "initial_debt", positive=True)
    require_decimal(nominal_annual, "nominal_annual")
    if nominal_annual < 0 or type(term_months) is not int or term_months < 1:
        raise ValueError("rate or term is invalid")
    return DerivedValue(
        _annuity_payment(initial_debt, nominal_annual, term_months),
        "derived",
        "monthly annuity present-value formula, rounded to cents",
        ("initial_debt", "nominal_annual", "term_months"),
    )


@financial_precision
def derive_annuity_term(
    initial_debt: Decimal,
    nominal_annual: Decimal,
    mandatory_installment: Decimal,
    *,
    search_through: int = 1200,
) -> DerivedTerm:
    """Return a term only when one searched term gives this rounded payment."""
    require_money(initial_debt, "initial_debt", positive=True)
    require_money(mandatory_installment, "mandatory_installment", positive=True)
    require_decimal(nominal_annual, "nominal_annual")
    if nominal_annual < 0 or type(search_through) is not int or search_through < 1:
        raise ValueError("rate or term search bound is invalid")
    if mandatory_installment <= quantize_cent(initial_debt * nominal_annual / Decimal(12)):
        raise ValueError("mandatory installment does not cover interest")
    matches = [
        months
        for months in range(1, search_through + 1)
        if _annuity_payment(initial_debt, nominal_annual, months) == mandatory_installment
    ]
    if len(matches) == 1:
        return DerivedTerm(matches[0], "derived")
    if len(matches) > 1:
        return DerivedTerm(None, "missing", "multiple terms produce the same rounded installment")
    return DerivedTerm(None, "missing", "no matching term within the explicit search range")
