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
    start:
        * The starting date of the generated range.
        * The first end is closed, therefore `start` is always included in the range.

    end:
        * The limit of the range.
        * If `end` is `int`, use `start` shifted `end` days.
        * If `end` is `datetime.date`, use it directly.
        * If `end` is `None`, use the value passed as `start`, and `start` defaults to
          `datetime.date.today()`.

    step:
        * Number of days advanced each iteration.
        * The sign of `step` is ignored and inferred from the range.

    include_last:
        * If `True`, turns the range from [start, end) to [start, end].
        * This argument is only used if `end` is `datetime.date`, otherwise, the range
          length is always `end`.

    """

    if end is None:
        start, end = Date.today(), start
    if isinstance(end, Date):
        end = (end - start).days
        end += include_last * sign(end, zero=1)
    return (start + DAY * i for i in range(0, end, sign(end, zero=1) * abs(step)))


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
