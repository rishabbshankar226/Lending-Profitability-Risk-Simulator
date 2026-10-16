"""Isolated Decimal arithmetic and bounded cancellation guard precision."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from decimal import (
    ROUND_HALF_EVEN,
    Context,
    Decimal,
    DecimalException,
    DivisionByZero,
    InvalidOperation,
    Overflow,
    Underflow,
    localcontext,
)
from functools import wraps

CALCULATION_PRECISION = 96
CANCELLATION_GUARD_DIGITS = 16
MAX_WORK_PRECISION = 4096
MAX_EXPONENT = 9999


@contextmanager
def numeric_context(precision: int = CALCULATION_PRECISION) -> Iterator[None]:
    if not CALCULATION_PRECISION <= precision <= MAX_WORK_PRECISION:
        raise ValueError("Calculation exceeds the supported Decimal precision budget.")
    context = Context(
        prec=precision, rounding=ROUND_HALF_EVEN, Emin=-MAX_EXPONENT,
        Emax=MAX_EXPONENT, capitals=1, clamp=0, flags=[],
        traps=[DivisionByZero, InvalidOperation, Overflow, Underflow],
    )
    with localcontext(context):
        try:
            yield
        except DecimalException as error:
            raise ValueError("Calculation is outside the supported finite Decimal domain.") from error


def cancellation_precision(value: Decimal) -> int:
    precision = CALCULATION_PRECISION + CANCELLATION_GUARD_DIGITS
    if value:
        precision += max(0, -value.adjusted())
    if precision > MAX_WORK_PRECISION:
        raise ValueError("Rate or probability exceeds the cancellation precision budget.")
    return precision


def finite_decimal(value: object, name: str) -> Decimal:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError(f"{name} must be a finite Decimal.")
    return value


def isolated[**P, R](function: Callable[P, R]) -> Callable[P, R]:
    @wraps(function)
    def invoke(*args: P.args, **kwargs: P.kwargs) -> R:
        with numeric_context():
            return function(*args, **kwargs)
    return invoke
