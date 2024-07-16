from calendar import monthrange
from datetime import date as Date
from datetime import timedelta as TimeDelta
from typing import Iterator, Self

import aamm.strings.match as match
from aamm.exceptions import DomainError, OperandError
from aamm.formats.exception import type_error
from aamm.std import ReadOnlyProperty, sign

DAY = TimeDelta(days=1)
WEEK = TimeDelta(days=7)


def date_range(
    start: Date,
    end: Date | int | None = None,
    step: int = 1,
    include_last: bool = True,
) -> Iterator[Date]:
    if end is None:
        start, end = Date.today(), start
    if isinstance(end, Date):
        end = (end - start).days + include_last
    return (start + DAY * i for i in range(0, end, step))


class YearMonth:
    is_yearmonth_string = match.create_matcher(r"^(-|\+)?\d{4}(0[1-9]|1[0-2])$")
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
                raise DomainError(subscript, -max_index, max_index, True, False)
            if subscript < 0:
                subscript += max_index
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
        if 1 <= month <= 12:
            self.value = 12 * year + month - 1
            return
        raise DomainError(month, 1, 12)

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
        return f"{type(self).__qualname__}({self.year}, {self.month})"

    def __str__(self) -> str:
        return (sign(y := self.year) == -1) * "-" + f"{abs(y):>04}{self.month:>02}"

    def __sub__(self, other: int | Self) -> Self | int:
        TypeSelf = type(self)
        if isinstance(other, int):
            return TypeSelf(self.value - other)
        elif isinstance(other, TypeSelf):
            return self.value - other.value
        raise OperandError(self, other, "-")

    @classmethod
    def from_date(cls, date: Date) -> Self:
        return cls(date.year, date.month)

    @classmethod
    def from_integer(cls, integer: int) -> Self:
        if not (-999901 <= integer <= 999912):
            raise DomainError(integer, -999901, 999912)

        s = sign(integer)
        i = abs(integer)
        year = i // 100
        month = i - year * 100

        try:
            return cls(s * year, month)
        except DomainError:
            raise ValueError(f"unable to interpret {integer}") from None

    @classmethod
    def from_string(cls, string: str) -> Self:
        if not cls.is_yearmonth_string(string):
            raise ValueError(f"unable to interpret '{string}'")
        return cls(int(string[:-2]), int(string[-2:]))

    def elapse(
        self, shift: int, length: int | None = None, step: int = 1
    ) -> Iterator[Self]:
        if length is None:
            shift, length = 0, shift
        for i in range(shift, length + shift, step):
            yield self + i

    @property
    def month(self) -> int:
        return self.value % 12 + 1

    @property
    def year(self) -> int:
        return self.value // 12

    @property
    def yearmonth(self) -> tuple[int]:
        return (self.year, self.month)
