from datetime import date as Date
from typing import Iterator

from aamm.schedule.constants import DAY
from aamm.std import sign


def date_range(
    start: Date,
    end: Date | int | None = None,
    step: int = 1,
    include_last: bool = True,
) -> Iterator[Date]:
    """
    DESCRIPTION
    -----------
    Generate a range of dates from `start` to `end` advancing `step` dates at a time.

    PARAMETERS
    ----------
    ### start: Date
        * the starting date of the generated range.
        * the first end is closed, therefore `start` is always included in the range.

    ### end: Date | int | None = None
        * the limit of the range.
        * if `end` is `int`, use `start` shifted `end` days.
        * if `end` is `datetime.date`, use it directly.
        * if `end` is `None`, use the value passed as `start` and `start` defaults to
          `datetime.date.today()`.

    ### step: int = 1
        * number of days advanced each iteration.
        * the sign of `step` is inferred, use positive integers only.

    ### include_last: bool = True
        * This argument is only used if `end` is `datetime.date`.
        * if `True`, turns the range from [start, end) to [start, end].

    """

    if end is None:
        start, end = Date.today(), start
    if isinstance(end, Date):
        end = (end - start).days
        end += include_last * sign(end, zero=1)
    return (start + DAY * i for i in range(0, end, sign(end, zero=1) * step))


def find_weekday(
    date: Date, weekday: int, index: int = 1, include_start: bool = False
) -> Date:
    if index == 0:
        return date

    shift = weekday - date.weekday()
    index_sign = sign(index)
    shift_sign = sign(shift)
    index -= (shift_sign == 0 and include_start) * index_sign
    shift += (shift_sign != index_sign) * 7 * index

    return date + DAY * shift
