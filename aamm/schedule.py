from calendar import monthrange
from datetime import date as Date
from datetime import timedelta as TimeDelta
from numbers import Number
from typing import Iterator, Self

from aamm.exception_message import index_error, operand_error, type_error
from aamm.meta import ReadOnlyProperty
from aamm.std import qualname, sign
from aamm.strings import pattern_match

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


DAY = TimeDelta(days=1)
WEEK = TimeDelta(weeks=1)

ZERO_DATE = Date(2000, 1, 1)


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def _elapse(difference: int, delta: int) -> range:
    range_sign = sign(difference, zero=1)
    difference += range_sign
    delta = range_sign * abs(delta)
    return range(0, difference, delta)


def elapse(start: Date, end: Date, delta: int = 1) -> Iterator[Date]:
    """Generate dates from `start` to `end` advancing `step` dates at a time."""
    return (start + DAY * i for i in _elapse((end - start).days, delta))


def find_weekday(
    start_date: Date, weekday: int, index: int = 1, include_start: bool = False
) -> Date:
    """
    DESCRIPTION
    -----------
    Find the nth date whose weekday matches `weekday`.

    PARAMETERS
    ----------
    start_date:
        * The starting date of the search.

    weekday:
        * An `int` representing the day of the week.
        * Ranges from [Monday = 0, Sunday = 6].

    index:
        * The index of the weekday to find.
        * Can be positive or negative but not 0.

    include_start:
        * If `True`, `start_date` counts for the indexing of the returned date.

    """

    if index == 0:
        raise ValueError("argument `index` can not be 0")

    shift = weekday - start_date.weekday()
    index_sign = sign(index)
    shift_sign = sign(shift)
    index -= (shift_sign == 0 and include_start) * index_sign
    shift += (shift_sign != index_sign) * 7 * index

    return start_date + DAY * shift


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


class YearMonth:
    """Date-like object, holds a pair year-month."""

    is_yearmonth_string = pattern_match.create_matcher(r"^\d{4}(0[1-9]|1[0-2])$")
    value = ReadOnlyProperty()

    def __add__(self, other: int) -> Self:
        if isinstance(other, int):
            return type(self)(self.value + other)
        raise TypeError(operand_error("+", self, other))

    def __eq__(self, other: Self | Number) -> bool:
        if isinstance(other, Number):
            return self.value == other
        return self.value == other.value

    def __ge__(self, other: Self) -> bool:
        return self.value >= other.value

    def __gt__(self, other: Self) -> bool:
        return self.value > other.value

    def __getitem__(self, subscript: int | slice) -> Date | Iterator[Date]:
        max_index = len(self)

        if isinstance(subscript, int):
            if not (-max_index <= subscript < max_index):
                raise IndexError(index_error(self, subscript))
            subscript += (subscript < 0) * max_index
            return Date(self.year, self.month, subscript + 1)

        elif isinstance(subscript, slice):
            return (
                Date(self.year, self.month, i + 1)
                for i in range(*subscript.indices(max_index))
            )

        raise TypeError(type_error(subscript, (int, slice)))

    def __hash__(self) -> int:
        return self.value

    def __iadd__(self, other: int) -> Self:
        return self.__add__(other)

    def __init__(self, year: int, month: int | None = None) -> None:
        if month is None:
            self.value = year
            return
        self.value = 12 * year + month - 1

    def __isub__(self, other: int | Self) -> Self | int:
        return self.__sub__(other)

    def __iter__(self) -> Iterator[Date]:
        return self[:]

    def __le__(self, other: Self) -> bool:
        return self.value <= other.value

    def __len__(self) -> int:
        return monthrange(self.year, self.month)[1]

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value

    def __ne__(self, other: Self) -> bool:
        return self.value != other.value

    def __repr__(self) -> str:
        return f"{qualname(self)}({self.year}, {self.month})"

    def __str__(self) -> str:
        return f"{self.year:>04}-{self.month:>02}"

    def __sub__(self, other: int | Self) -> Self | int:
        if isinstance(other, cls := type(self)):
            return self.value - other.value
        elif isinstance(other, int):
            return cls(self.value - other)
        raise TypeError(operand_error("-", self, other))

    def current_month() -> int:
        """Return today's month."""
        return Date.today().month

    def current_year() -> int:
        """Return today's year."""
        return Date.today().year

    def elapse(self, end: Self, delta: int = 1) -> Iterator[Self]:
        """Generate `YearMonth` objects going from `self` to `end`."""
        return (self + i for i in _elapse(end.value - self.value, delta))

    @classmethod
    def from_date(cls, date: Date | None = None) -> Self:
        """Construct from an object with year and month properties."""
        if date is None:
            date = Date.today()
        return cls(date.year, date.month)

    @classmethod
    def from_integer(cls, integer: int) -> Self:
        """Construct from a valid `int` object YYYYMM."""
        return cls.from_string(f"{integer:>06}")

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Construct from a valid `str` object."""
        if not cls.is_yearmonth_string(string):
            raise ValueError(f"unable to interpret '{string}' as {cls.__qualname__}")
        return cls(int(string[:-2]), int(string[-2:]))

    @property
    def month(self) -> int:
        return self.value % 12 + 1

    def raw_string(self) -> str:
        """Return a raw representation of `self` as a string in the format 'YYYYMM'."""
        return f"{self.year:>04}{self.month:>02}"

    @property
    def year(self) -> int:
        return self.value // 12

    @property
    def yearmonth(self) -> tuple[int, int]:
        return (self.year, self.month)
