from datetime import date as Date
from datetime import timedelta as TimeDelta
from typing import Generator

DAY = TimeDelta(days=1)
WEEK = TimeDelta(days=7)


def date_range(
    start: Date,
    end: Date | int | None = None,
    step: int = 1,
    include_last: bool = True,
) -> Generator:
    if end is None:
        start, end = Date.today(), start
    if isinstance(end, Date):
        end = (end - start).days + include_last
    return (start + DAY * i for i in range(0, end, step))
