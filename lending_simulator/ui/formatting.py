"""Human-readable units without changing exact financial classifications."""

from decimal import Decimal
from math import isfinite

from lending_simulator.formatting import percent as percent
from lending_simulator.numeric import isolated
from lending_simulator.ui.state import FIELDS


def _missing(value) -> bool:
    return value is None or (not value.is_finite() if isinstance(value, Decimal) else not isfinite(value))


@isolated
def money(value: Decimal | float | None) -> str:
    if _missing(value):
        return 'Unavailable'
    if value == 0:
        return '$0'
    if 0 < abs(value) < 1:
        return '(<$1)' if value < 0 else '<$1'
    return f'(${abs(value):,.0f})' if value < 0 else f'${value:,.0f}'


@isolated
def points(value: Decimal | None) -> str:
    if _missing(value):
        return 'Unavailable'
    amount = '<0.01' if 0 < abs(value) < Decimal('.01') else f'{abs(value):.2f}'
    return f'{"−" if value < 0 else ""}{amount} pp'


@isolated
def multiple(value: Decimal) -> str:
    return f'{value.normalize():f}×'


@isolated
def assumption_value(field: str, value) -> str:
    """Review committed inputs with their units and original decimal precision."""
    if _missing(value):
        return 'Enter a value'
    if field == 'default_stress':
        return multiple(value)
    if field == 'recovery_lag':
        return f'{value} months'
    if next(scale for name, _, _, scale in FIELDS if name == field) == 100:
        return f'{(value * 100).normalize():f}%'
    amount = f'{abs(value).normalize():,f}'
    return f'(${amount})' if value < 0 else f'${amount}'
