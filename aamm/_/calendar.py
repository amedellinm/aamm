from collections.abc import Iterator
from datetime import date as Date
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
from numbers import Number
from typing import Literal

import aamm.logging.formats as fmts
from aamm.meta import ReadOnlyProperty
from aamm.string import create_matcher

try:
    from typing import Self
except ImportError:
    from typing import Any as Self


DAY = TimeDelta(days=1)
WEEK = TimeDelta(weeks=1)


def _elapse(difference: int, delta: int) -> range:
    range_sign = -1 if difference < 0 else 1
    difference += range_sign
    delta = range_sign * abs(delta)
    return range(0, difference, delta)


def elapse(start: Date, end: Date, delta: int = 1) -> Iterator[Date]:
    """Generate dates from `start` to `end` advancing `step` dates at a time."""
    difference = (
        end - int(end and end // abs(end))
        if isinstance(end, int)
        else (end - start).days
    )
    return (start + DAY * i for i in _elapse(difference, delta))


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
        * If `True`, `start_date` counts towards the indexing of the returned date.

    """

    if index == 0:
        raise ValueError("argument `index` can not be 0")

    shift = weekday - start_date.weekday()
    index_sign = -1 if index < 0 else 1
    shift_sign = shift and (-1 if shift < 0 else 1)
    index -= (shift_sign == 0 and include_start) * index_sign
    shift += (shift_sign != index_sign) * 7 * index

    return start_date + DAY * shift


def first_isodate(year: int) -> Date:
    """Return the first date in the isoyear."""
    return parse_string(f"{year:>04}011", r"%G%V%u")


def is_leap(year):
    """Return True for leap years, False for non-leap years."""
    return year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)


def month_days(year: int, month: int) -> int:
    """Return the number of days in a year-month."""
    parity = (month + (month > 7)) % 2
    february = month == 2
    return (30 + parity) - (2 * february >> is_leap(year))


def parse_date(date: Date, format_codes: str) -> str:
    """Parse a date into a string. Check the `strftime` Format Codes online."""
    return DateTime.strftime(date, format_codes)


def parse_string(string: str, format_codes: str) -> Date:
    """Parse a string into a date. Check the `strptime` Format Codes online."""
    return DateTime.strptime(string, format_codes).date()


class DateValue:
    value = ReadOnlyProperty()

    def __add__(self, other: int) -> Self:
        """Create a new instance with `value` equal to `self.value + other`."""
        if isinstance(other, int):
            return type(self)(self.value + other)
        raise TypeError(operand_error("+", self, other))

    def __eq__(self, other: Self | Number) -> bool:
        """Test equality of type and value."""
        if isinstance(other, Number):
            return self.value == other
        return isinstance(other, type(self)) and self.value == other.value

    def __ge__(self, other: Self) -> bool:
        """Compare using `self.value`."""
        return self.value >= other.value

    def __gt__(self, other: Self) -> bool:
        """Compare using `self.value`."""
        return self.value > other.value

    def __hash__(self) -> int:
        """Use `self.value`."""
        return self.value

    def __iadd__(self, other: int) -> Self:
        """Fallback to `self.__add__`."""
        return self.__add__(other)

    def __isub__(self, other: int | Self) -> Self | int:
        """Fallback to `self.__sub__`."""
        return self.__sub__(other)

    def __iter__(self) -> Iterator[Date]:
        """Iterate with `self.__getitem__`."""
        return self[:]

    def __le__(self, other: Self) -> bool:
        """Compare using `self.value`."""
        return self.value <= other.value

    def __lt__(self, other: Self) -> bool:
        """Compare using `self.value`."""
        return self.value < other.value

    def __ne__(self, other: Self) -> bool:
        """Compare using `self.value`."""
        return self.value != other.value

    def __str__(self) -> str:
        """Cast to `int`, then to `str`."""
        return str(int(self))

    def __sub__(self, other: int | Self) -> Self | int:
        """
        Create a new instance with `value` equal to `self.value - other`.
        If `other` is of the same type as `self`, return an `int` representing the
        difference between them in the underlying unit.

        """
        if isinstance(other, cls := type(self)):
            return self.value - other.value
        elif isinstance(other, int):
            return cls(self.value - other)
        raise TypeError(fmts.operand_error("-", self, other))

    @classmethod
    def current(cls) -> Self:
        """Return today's `cls` instance."""
        return cls.from_date(Date.today())

    def elapse(self, end: int | Self, delta: int = 1) -> Iterator[Self]:
        """Generate `type(self)` objects going from `self` to `end`."""
        difference = (
            end - int(end and end // abs(end))
            if isinstance(end, int)
            else end.value - self.value
        )

        return (self + i for i in _elapse(difference, delta))

    @classmethod
    def from_integer(cls, integer: int) -> Self:
        """Construct from a valid `int` object YYYYMM."""
        return cls.from_string(f"{integer:>06}")


class YearMonth(DateValue):
    """Date-like object, holds a pair year-month."""

    is_valid_string = create_matcher(r"^\d{4}(0[1-9]|1[0-2])$")

    def __getitem__(self, subscript: int | slice) -> Date | Iterator[Date]:
        """Return/Yield the dates of the month."""
        max_index = len(self)

        if isinstance(subscript, int):
            if not (-max_index <= subscript < max_index):
                raise IndexError(fmts.index_error(self, subscript))
            subscript += (subscript < 0) * max_index
            return Date(self.year, self.month, subscript + 1)

        elif isinstance(subscript, slice):
            return (
                Date(self.year, self.month, i + 1)
                for i in range(*subscript.indices(max_index))
            )

        raise TypeError(type_error(subscript, (int, slice)))

    def __init__(self, year: int, month: int = None) -> None:
        """If `month is None`, set `self.value` to `year`."""
        if month is None:
            self.value = year
            return
        elif not (1 <= month <= 12):
            raise ValueError(f"expected [1, 12] for `month`, got {month}")
        self.value = 12 * year + month - 1

    def __int__(self) -> int:
        """Concatenate year and month to form an `int`. The month is padded with a 0."""
        return 100 * self.year + self.month

    def __len__(self) -> int:
        """Return the number of days in the month."""
        return month_days(*self.yearmonth)

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({self.year}, {self.month})"

    @classmethod
    def from_date(cls, date: Date) -> Self:
        """Construct from an object with year and month properties."""
        return cls(date.year, date.month)

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Construct from a valid `str` object."""
        if not cls.is_valid_string(string):
            raise ValueError(f"unable to interpret '{string}' as {cls.__qualname__}")
        return cls(int(string[:-2]), int(string[-2:]))

    @property
    def month(self) -> int:
        return self.value % 12 + 1

    @property
    def year(self) -> int:
        return self.value // 12

    @property
    def yearmonth(self) -> tuple[int, int]:
        return (self.year, self.month)


class YearWeek(DateValue):
    """Date-like object, holds a pair year-week."""

    def __getitem__(self, subscript: int | slice) -> Date | Iterator[Date]:
        """Return/Yield the dates of the week."""
        if isinstance(subscript, int):
            if -7 <= subscript < 7:
                subscript += (subscript < 0) * 7 + 1
                return Date.fromisocalendar(self.year, self.week, subscript)
            raise IndexError(fmts.index_error(self, subscript))

        elif isinstance(subscript, slice):
            return (
                Date.fromisocalendar(self.year, self.week, i + 1)
                for i in range(*subscript.indices(7))
            )

        raise TypeError(type_error(subscript, (int, slice)))

    def __init__(self, year: int, week: int = None):
        if week is None:
            self.value = year
            return
        self.value = (Date.fromisocalendar(year, week, 1).toordinal() - 1) // 7

    def __int__(self) -> int:
        """Concatenate year and week to form an `int`. The week is padded with a 0."""
        return 100 * self.year + self.week

    def __len__(self) -> Literal[7]:
        """Return the constant `7`."""
        return 7

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({self.year}, {self.week})"

    @classmethod
    def from_date(cls, date: Date) -> Self:
        """Construct from an object with the `isocalendar` method."""
        return cls(*date.isocalendar()[:2])

    @classmethod
    def from_string(cls, string: str) -> Self:
        """Construct from a valid `str` object."""
        year = int(string[:-2])
        week = int(string[-2:])

        Date.fromisocalendar(year, week, 1)
        # raise ValueError(f"unable to interpret '{string}' as {cls.__qualname__}")
        return cls(year, week)

    @property
    def week(self) -> int:
        return Date.fromordinal(self.value * 7 + 1).isocalendar().week

    @property
    def year(self) -> int:
        return Date.fromordinal(self.value * 7 + 1).isocalendar().year

    @property
    def yearweek(self) -> tuple[int, int]:
        return (self.year, self.week)
