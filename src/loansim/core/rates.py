"""Deterministic monthly rate paths with explicit observation provenance."""

from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal, TypeAlias

from loansim.core.metrics import simplified_effective_annual
from loansim.core.models import financial_precision, require_decimal

ObservationKind: TypeAlias = Literal["historical", "hypothetical"]
SourceKind: TypeAlias = Literal["fixed", "historical", "hypothetical", "constant_future"]


def monthly_date(start: date, month_offset: int) -> date:
    """Shift from the original date, retaining a month-end anchor."""
    if type(start) is not date or type(month_offset) is not int or month_offset < 0:
        raise ValueError("start and month_offset are invalid")
    absolute_month = start.year * 12 + start.month - 1 + month_offset
    year, zero_month = divmod(absolute_month, 12)
    month = zero_month + 1
    original_last_day = monthrange(start.year, start.month)[1]
    destination_last_day = monthrange(year, month)[1]
    day = (
        destination_last_day
        if start.day == original_last_day
        else min(start.day, destination_last_day)
    )
    return date(year, month, day)


@dataclass(frozen=True, slots=True)
class FixedRate:
    nominal_annual: Decimal
    source_name: str = "user input"

    def __post_init__(self) -> None:
        require_decimal(self.nominal_annual, "nominal_annual")
        if self.nominal_annual < 0 or not self.source_name.strip():
            raise ValueError("fixed rate or source is invalid")


@dataclass(frozen=True, slots=True)
class RateObservation:
    period: int
    index_annual: Decimal
    kind: ObservationKind
    source_name: str
    published_on: date | None = None
    observed_on: date | None = None

    def __post_init__(self) -> None:
        if type(self.period) is not int or self.period < 1:
            raise ValueError("period must be positive")
        require_decimal(self.index_annual, "index_annual")
        if self.kind not in ("historical", "hypothetical") or not self.source_name.strip():
            raise ValueError("observation kind or source is invalid")
        if self.kind == "historical":
            if type(self.published_on) is not date or type(self.observed_on) is not date:
                raise ValueError("historical observation dates are required")
            if self.observed_on > self.published_on:
                raise ValueError("historical observation postdates publication")


@dataclass(frozen=True, slots=True)
class VariableRate:
    index_name: str
    margin: Decimal
    observations: tuple[RateObservation, ...]
    as_of_date: date

    def __post_init__(self) -> None:
        if not self.index_name.strip() or type(self.as_of_date) is not date:
            raise ValueError("index name and as_of_date are required")
        require_decimal(self.margin, "margin")
        if not isinstance(self.observations, tuple) or not self.observations:
            raise ValueError("at least one monthly observation is required")


@dataclass(frozen=True, slots=True)
class PeriodicallyFixedRate:
    initial_nominal_annual: Decimal
    fixed_months: int
    follow_on: FixedRate | VariableRate

    def __post_init__(self) -> None:
        require_decimal(self.initial_nominal_annual, "initial_nominal_annual")
        if (
            self.initial_nominal_annual < 0
            or type(self.fixed_months) is not int
            or self.fixed_months < 1
        ):
            raise ValueError("initial fixed period is invalid")
        if not isinstance(self.follow_on, (FixedRate, VariableRate)):
            raise ValueError("an explicit follow-on rate plan is required")


RatePlan: TypeAlias = FixedRate | VariableRate | PeriodicallyFixedRate


@dataclass(frozen=True, slots=True)
class PeriodRate:
    period: int
    period_start: date
    payment_date: date
    nominal_annual: Decimal
    effective_annual: Decimal
    source_kind: SourceKind
    source_name: str
    index_name: str | None = None
    index_annual: Decimal | None = None
    margin: Decimal | None = None
    observed_on: date | None = None
    published_on: date | None = None


def _period_rate(
    period: int,
    start: date,
    nominal: Decimal,
    source_kind: SourceKind,
    source_name: str,
    *,
    index_name: str | None = None,
    observation: RateObservation | None = None,
    margin: Decimal | None = None,
) -> PeriodRate:
    if nominal < 0:
        raise ValueError("negative total nominal rate is unsupported")
    return PeriodRate(
        period=period,
        period_start=monthly_date(start, period - 1),
        payment_date=monthly_date(start, period),
        nominal_annual=nominal,
        effective_annual=simplified_effective_annual(nominal),
        source_kind=source_kind,
        source_name=source_name,
        index_name=index_name,
        index_annual=observation.index_annual if observation else None,
        margin=margin,
        observed_on=observation.observed_on if observation else None,
        published_on=observation.published_on if observation else None,
    )


def _variable_rows(
    plan: VariableRate, start: date, first_period: int, last_period: int
) -> tuple[PeriodRate, ...]:
    observations = sorted(plan.observations, key=lambda point: point.period)
    expected = list(range(first_period, observations[-1].period + 1))
    if [point.period for point in observations] != expected:
        raise ValueError("monthly rate path has a missing or duplicate interior observation")
    by_period = {point.period: point for point in observations}
    rows = []
    last_observation = observations[0]
    for period in range(first_period, last_period + 1):
        period_start = monthly_date(start, period - 1)
        observation = by_period.get(period)
        if observation is not None:
            if observation.kind == "historical":
                if observation.published_on is None or observation.published_on > period_start:
                    raise ValueError("historical rate was not published by the period start")
                if observation.published_on > plan.as_of_date:
                    raise ValueError("historical rate was unavailable at the as-of date")
            last_observation = observation
            kind: SourceKind = observation.kind
        else:
            if period_start <= plan.as_of_date:
                raise ValueError("missing historical monthly rate")
            observation = last_observation
            kind = "constant_future"
        rows.append(
            _period_rate(
                period,
                start,
                observation.index_annual + plan.margin,
                kind,
                observation.source_name,
                index_name=plan.index_name,
                observation=observation,
                margin=plan.margin,
            )
        )
    return tuple(rows)


@financial_precision
def rate_schedule(plan: RatePlan, term_months: int, start_date: date) -> tuple[PeriodRate, ...]:
    """Resolve all model periods and reject unavailable historical observations."""
    if type(term_months) is not int or term_months < 1 or type(start_date) is not date:
        raise ValueError("term and start_date are invalid")
    if isinstance(plan, FixedRate):
        return tuple(
            _period_rate(period, start_date, plan.nominal_annual, "fixed", plan.source_name)
            for period in range(1, term_months + 1)
        )
    if isinstance(plan, VariableRate):
        return _variable_rows(plan, start_date, 1, term_months)
    if isinstance(plan, PeriodicallyFixedRate):
        fixed_end = min(plan.fixed_months, term_months)
        fixed_rows = tuple(
            _period_rate(period, start_date, plan.initial_nominal_annual, "fixed", "fixed period")
            for period in range(1, fixed_end + 1)
        )
        if fixed_end == term_months:
            return fixed_rows
        if isinstance(plan.follow_on, FixedRate):
            follow_on_rows = tuple(
                _period_rate(
                    period,
                    start_date,
                    plan.follow_on.nominal_annual,
                    "hypothetical",
                    plan.follow_on.source_name,
                )
                for period in range(fixed_end + 1, term_months + 1)
            )
        else:
            follow_on_rows = _variable_rows(plan.follow_on, start_date, fixed_end + 1, term_months)
        return fixed_rows + follow_on_rows
    raise ValueError("unsupported rate plan")
