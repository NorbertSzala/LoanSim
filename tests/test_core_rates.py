"""Rate-path and calendar-label behavior under equal monthly model periods."""

from datetime import date
from decimal import Decimal

import pytest

from loansim.core.metrics import simplified_effective_annual
from loansim.core.rates import (
    FixedRate,
    PeriodicallyFixedRate,
    RateObservation,
    VariableRate,
    monthly_date,
    rate_schedule,
)


def test_month_end_dates_rebound_after_february() -> None:
    start = date(2026, 1, 31)

    assert monthly_date(start, 1) == date(2026, 2, 28)
    assert monthly_date(start, 2) == date(2026, 3, 31)
    assert monthly_date(start, 3) == date(2026, 4, 30)


def test_fixed_rate_and_simplified_effective_annual_reference() -> None:
    rows = rate_schedule(FixedRate(Decimal("0.12")), 2, date(2026, 1, 1))

    assert [row.nominal_annual for row in rows] == [Decimal("0.12")] * 2
    assert rows[0].effective_annual == Decimal("0.126825030131969720661201")
    assert simplified_effective_annual(Decimal("0")) == Decimal("0")


def test_variable_path_resets_and_labels_future_continuation() -> None:
    plan = VariableRate(
        index_name="POLSTR 1M compounded",
        margin=Decimal("0.02"),
        observations=(
            RateObservation(
                1, Decimal("0.03"), "historical", "official", date(2026, 1, 30), date(2026, 1, 29)
            ),
            RateObservation(
                2, Decimal("0.04"), "historical", "official", date(2026, 2, 27), date(2026, 2, 26)
            ),
        ),
        as_of_date=date(2026, 3, 1),
    )

    rows = rate_schedule(plan, 3, date(2026, 1, 31))

    assert [row.nominal_annual for row in rows] == [
        Decimal("0.05"),
        Decimal("0.06"),
        Decimal("0.06"),
    ]
    assert rows[0].index_annual == Decimal("0.03")
    assert rows[2].source_kind == "constant_future"
    assert rows[2].source_name == "official"


def test_periodic_fixed_rate_has_explicit_hypothetical_follow_on() -> None:
    plan = PeriodicallyFixedRate(Decimal("0.06"), 2, FixedRate(Decimal("0.08")))

    rows = rate_schedule(plan, 3, date(2026, 1, 1))

    assert [row.nominal_annual for row in rows] == [
        Decimal("0.06"),
        Decimal("0.06"),
        Decimal("0.08"),
    ]
    assert rows[2].source_kind == "hypothetical"


def test_periodic_fixed_rate_can_follow_an_explicit_variable_index_path() -> None:
    follow_on = VariableRate(
        "INDEX",
        Decimal("0.02"),
        (
            RateObservation(
                2, Decimal("0.04"), "historical", "source", date(2026, 1, 31), date(2026, 1, 30)
            ),
        ),
        date(2026, 2, 1),
    )
    plan = PeriodicallyFixedRate(Decimal("0.05"), 1, follow_on)

    rows = rate_schedule(plan, 3, date(2026, 1, 1))

    assert [row.nominal_annual for row in rows] == [
        Decimal("0.05"),
        Decimal("0.06"),
        Decimal("0.06"),
    ]
    assert rows[1].source_kind == "historical"
    assert rows[2].source_kind == "constant_future"


@pytest.mark.parametrize(
    "observations",
    [
        (
            RateObservation(
                2, Decimal("0.03"), "historical", "official", date(2026, 2, 1), date(2026, 1, 31)
            ),
        ),
        (
            RateObservation(
                1, Decimal("0.03"), "historical", "official", date(2026, 1, 1), date(2025, 12, 31)
            ),
            RateObservation(
                3, Decimal("0.04"), "historical", "official", date(2026, 3, 1), date(2026, 2, 28)
            ),
        ),
        (
            RateObservation(
                1, Decimal("0.03"), "historical", "official", date(2026, 2, 1), date(2026, 1, 31)
            ),
        ),
    ],
)
def test_missing_or_late_historical_observations_are_rejected(
    observations: tuple[RateObservation, ...],
) -> None:
    plan = VariableRate("INDEX", Decimal("0.02"), observations, date(2026, 3, 1))

    with pytest.raises(ValueError):
        rate_schedule(plan, 3, date(2026, 1, 1))


def test_negative_total_nominal_rate_is_rejected() -> None:
    plan = VariableRate(
        "INDEX",
        Decimal("0.01"),
        (RateObservation(1, Decimal("-0.02"), "hypothetical", "scenario"),),
        date(2025, 12, 31),
    )

    with pytest.raises(ValueError, match="negative"):
        rate_schedule(plan, 1, date(2026, 1, 1))


def test_missing_historical_tail_is_rejected_before_as_of_date() -> None:
    plan = VariableRate(
        "INDEX",
        Decimal("0.02"),
        (
            RateObservation(
                1, Decimal("0.03"), "historical", "source", date(2025, 12, 31), date(2025, 12, 30)
            ),
        ),
        date(2026, 3, 1),
    )

    with pytest.raises(ValueError, match="missing historical"):
        rate_schedule(plan, 2, date(2026, 1, 1))


def test_observation_published_after_as_of_date_is_rejected() -> None:
    plan = VariableRate(
        "INDEX",
        Decimal("0.02"),
        (
            RateObservation(
                1, Decimal("0.03"), "historical", "source", date(2025, 12, 31), date(2025, 12, 30)
            ),
        ),
        date(2025, 12, 30),
    )

    with pytest.raises(ValueError, match="as-of"):
        rate_schedule(plan, 1, date(2026, 1, 1))
