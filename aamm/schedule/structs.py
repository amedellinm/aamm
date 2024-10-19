from calendar import monthrange
from datetime import date as Date
from typing import Iterator, Self

import aamm.strings.match as match
from aamm.exceptions import OperandError, assert_domain
from aamm.exceptions.formats import index_error, type_error
from aamm.meta import ReadOnlyProperty
from aamm.std import qualname, sign


class YearMonth:
    """Date-like object, holds a pair year-month."""

    is_yearmonth_string = match.create_matcher(r"^\d{4}(0[1-9]|1[0-2])$")
    value = ReadOnlyProperty()

    def __add__(self, other: int) -> Self:
        if isinstance(other, int):
            return type(self)(self.value + other)
        raise OperandError(self, other, "+")

    def __eq__(self, other: Self) -> bool:
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
        assert_domain("year", year, 0, 9999),
        assert_domain("month", month, 1, 12),
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
        if isinstance(other, TypeSelf := type(self)):
            return self.value - other.value
        elif isinstance(other, int):
            return TypeSelf(self.value - other)
        raise OperandError(self, other, "-")

    def current_month() -> int:
        """Return today's month."""
        return Date.today().month

    def current_year() -> int:
        """Return today's year."""
        return Date.today().year

    def elapse(self, yearmonth: Self, step: int = 1) -> Iterator[Self]:
        """Generate `YearMonth` objects going from `self` to `yearmonth`."""
        length = yearmonth.value - self.value
        s = sign(length)
        length += s
        return self.range(length, s * abs(step))

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

    def range(self, length: int, step: int = 1) -> Iterator[Self]:
        """Generate `YearMonth` objects going from `self` to `self + length`."""
        return (self + i for i in range(0, length, sign(length) * abs(step)))

    def raw_string(self) -> str:
        """Return a raw representation of `self` as a string in the format 'YYYYMM'."""
        return f"{self.year:>04}{self.month:>02}"

    @property
    def year(self) -> int:
        return self.value // 12

    @property
    def yearmonth(self) -> tuple[int, int]:
        return (self.year, self.month)
