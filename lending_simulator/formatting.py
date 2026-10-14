"""Pure percentage labels shared by the workbench and decision briefs."""

from decimal import Decimal
from math import isnan


def percent(value: Decimal | float | None) -> str:
    if value is None or (value.is_nan() if isinstance(value, Decimal) else isnan(value)):
        return 'Unavailable'
    magnitude = value.copy_abs() if isinstance(value, Decimal) else abs(value)
    if 0 < magnitude < Decimal('.0001'):
        return '−<0.01%' if value < 0 else '<0.01%'
    return f'{0 if value == 0 else value:.2%}'
