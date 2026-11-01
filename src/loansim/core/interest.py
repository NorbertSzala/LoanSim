"""Interest-accrual boundary for the approved equal-monthly-period convention."""

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from typing import TypeAlias

from loansim.core.models import financial_precision, quantize_cent, require_decimal

InterestAccrual: TypeAlias = Callable[[Decimal, Decimal, date, date], Decimal]


@financial_precision
def monthly_nominal_interest(
    balance: Decimal, nominal_annual: Decimal, period_start: date, payment_date: date
) -> Decimal:
    """Settle one equal model month; dates are retained for later conventions."""
    require_decimal(balance, "balance")
    require_decimal(nominal_annual, "nominal_annual")
    if balance < 0 or nominal_annual < 0:
        raise ValueError("balance and total nominal rate must be nonnegative")
    if (
        type(period_start) is not date
        or type(payment_date) is not date
        or payment_date <= period_start
    ):
        raise ValueError("payment_date must follow period_start")
    return quantize_cent(balance * nominal_annual / Decimal(12))
