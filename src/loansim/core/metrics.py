"""Clearly labeled informational rate metrics for equal monthly periods."""

from decimal import Decimal, localcontext

from loansim.core.models import require_decimal


def simplified_effective_annual(nominal_annual: Decimal) -> Decimal:
    """Convert a nominal annual rate to monthly-compounded annual interest."""
    require_decimal(nominal_annual, "nominal_annual")
    if nominal_annual < 0:
        raise ValueError("negative total nominal rate is unsupported")
    with localcontext() as context:
        context.prec = 50
        return (Decimal(1) + nominal_annual / Decimal(12)) ** 12 - Decimal(1)
