from calendar import isleap as is_leap
from calendar import monthrange
from collections.abc import Iterator
from datetime import date as Date
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta
from numbers import Number

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


def date_range(start: Date, stop: int, step: int = 1) -> Iterator[Date]:
    """
    Iterate like `range` but using `datetime.date` instead of `int`s. `start` is the
    beginning of the range. The sign of `step` is ignored, instead it is inferred
    from `stop`.

    """
    step = (-1 if stop < 0 else 1) * abs(step)
    return (start + DAY * i for i in range(0, stop, step))


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


def parse_date(date: Date, format_codes: str) -> str:
    """Parse a date into a string. Check the `strftime` Format Codes online."""
    return DateTime.strftime(date, format_codes)


def parse_string(string: str, format_codes: str) -> Date:
    """Parse a string into a date. Check the `strptime` Format Codes online."""
    return DateTime.strptime(string, format_codes).date()


class DateValue:
    value = ReadOnlyProperty()

    def __add__(self, other: int) -> Self:
        if isinstance(other, int):
            return type(self)(self.value + other)
        raise TypeError(operand_error("+", self, other))

    def __eq__(self, other: Self | Number) -> bool:
        if isinstance(other, Number):
            return self.value == other
        return isinstance(other, type(self)) and self.value == other.value

    def __ge__(self, other: Self) -> bool:
        return self.value >= other.value

    def __gt__(self, other: Self) -> bool:
        return self.value > other.value

    def __hash__(self) -> int:
        return self.value

    def __iadd__(self, other: int) -> Self:
        return self.__add__(other)

    def __isub__(self, other: int | Self) -> Self | int:
        return self.__sub__(other)

    def __iter__(self) -> Iterator[Date]:
        return self[:]

    def __le__(self, other: Self) -> bool:
        return self.value <= other.value

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value

    def __ne__(self, other: Self) -> bool:
        return self.value != other.value

    def __str__(self) -> str:
        return str(int(self))

    def __sub__(self, other: int | Self) -> Self | int:
        if isinstance(other, cls := type(self)):
            return self.value - other.value
        elif isinstance(other, int):
            return cls(self.value - other)
        raise TypeError(fmts.operand_error("-", self, other))

    @classmethod
    def current(cls) -> Self:
        """Return today's `cls`."""
        return cls.from_date(Date.today())

    def elapse(self, end: Self, delta: int = 1) -> Iterator[Self]:
        """Generate `YearMonth` objects going from `self` to `end`."""
        return (self + i for i in _elapse(end.value - self.value, delta))

    @classmethod
    def from_integer(cls, integer: int) -> Self:
        """Construct from a valid `int` object YYYYMM."""
        return cls.from_string(f"{integer:>06}")

    def range(self, stop: int, step: int = 1) -> Iterator[Self]:
        """
        Iterate like `range` but using `type(self)` instead of `int`s. `self` is the
        beginning of the range. The sign of `step` is ignored, instead it is inferred
        from `stop`.

        """
        step = (-1 if stop < 0 else 1) * abs(step)
        return (self + i for i in range(0, stop, step))


class YearMonth(DateValue):
    """Date-like object, holds a pair year-month."""

    is_valid_string = create_matcher(r"^\d{4}(0[1-9]|1[0-2])$")

    def __getitem__(self, subscript: int | slice) -> Date | Iterator[Date]:
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

    def __init__(self, years: int, months: int | None = None) -> None:
        if months is None:
            self.value = years
            return
        self.value = 12 * years + months - 1

    def __int__(self) -> int:
        return 100 * self.year + self.month

    def __len__(self) -> int:
        return monthrange(self.year, self.month)[1]

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({self.year}, {self.month})"

    def current_month() -> int:
        """Return today's month."""
        return Date.today().month

    def current_year() -> int:
        """Return today's year."""
        return Date.today().year

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
        return 100 * self.year + self.week

    def __len__(self) -> int:
        return 7

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}({self.year}, {self.week})"

    def current_month() -> int:
        """Return today's isomonth."""
        return Date.today().isocalendar().month

    def current_week() -> int:
        """Return today's isoweek."""
        return Date.today().isocalendar().week

    def current_year() -> int:
        """Return today's isoyear."""
        return Date.today().isocalendar().year

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
