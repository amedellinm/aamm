from datetime import date as Date

from aamm import calendar, testing
from aamm.testing import asserts


def test_elapse_generic(elapse, x1, x2, x3):
    asserts.equal(tuple(elapse(x1, x3)), (x1, x2, x3))
    asserts.equal(tuple(elapse(x3, x1)), (x3, x2, x1))

    asserts.equal(tuple(elapse(x1, x3, 2)), (x1, x3))
    asserts.equal(tuple(elapse(x3, x1, 2)), (x3, x1))
    asserts.equal(tuple(elapse(x3, x1, -2)), (x3, x1))


class TestCalendar(testing.TestSuite):
    @testing.subjects(
        calendar.Date,
        calendar.DateTime,
        calendar.parse_date,
        calendar.parse_string,
    )
    def test_aliases(self):
        """Aliases for symbols in the standard library do not require testing."""

    @testing.subjects(calendar.date_range)
    def test_date_range(self):
        origin = calendar.Date(2000, 1, 1)

        expected = (origin, origin + 1 * calendar.DAY, origin + 2 * calendar.DAY)
        obtained = tuple(calendar.date_range(origin, 3))
        asserts.equal(expected, obtained)

        expected = (origin, origin - 1 * calendar.DAY, origin - 2 * calendar.DAY)
        obtained = tuple(calendar.date_range(origin, -3))
        asserts.equal(expected, obtained)

        expected = (origin, origin + 2 * calendar.DAY)
        obtained = tuple(calendar.date_range(origin, 3, 2))
        asserts.equal(expected, obtained)

    @testing.subjects(calendar.elapse)
    def test_elapse(self):
        d1 = Date(2000, 1, 1)
        d2 = Date(2000, 1, 2)
        d3 = Date(2000, 1, 3)

        test_elapse_generic(calendar.elapse, d1, d2, d3)

    @testing.subjects(calendar.find_weekday)
    def test_find_weekday(self):
        d1 = Date(2000, 1, 1)
        d2 = Date(2000, 1, 2)
        d3 = Date(2000, 1, 8)

        asserts.equal(calendar.find_weekday(d1, d1.weekday()), d3)
        asserts.equal(
            calendar.find_weekday(d1, d1.weekday(), +1, True),
            calendar.find_weekday(d1, d1.weekday(), -1, True),
        )

        asserts.equal(calendar.find_weekday(d1, d2.weekday()), d2)
        asserts.equal(calendar.find_weekday(d1, d2.weekday(), 1, True), d2)

        asserts.equal(calendar.find_weekday(d2, d1.weekday()), d3)
        asserts.equal(calendar.find_weekday(d2, d1.weekday(), -1), d1)
        asserts.equal(calendar.find_weekday(d2, d1.weekday(), -1, True), d1)

        asserts.equal(calendar.find_weekday(d1, d1.weekday(), 1, True), d1)
        asserts.equal(calendar.find_weekday(d3, d3.weekday(), -1), d1)
        asserts.equal(calendar.find_weekday(d3, d3.weekday(), -1, True), d3)

        asserts.equal(calendar.find_weekday(d1, d1.weekday(), 2, True), d3)
        asserts.equal(calendar.find_weekday(d3, d3.weekday(), -2, True), d1)

        asserts.raise_exception(ValueError, calendar.find_weekday, d1, d1.weekday(), 0)

    @testing.subjects(calendar.first_isodate)
    def test_first_isodate(self):
        test_cases = {
            1995: calendar.Date(1995, 1, 2),
            1996: calendar.Date(1996, 1, 1),
            1997: calendar.Date(1996, 12, 30),
            1998: calendar.Date(1997, 12, 29),
            1999: calendar.Date(1999, 1, 4),
            2000: calendar.Date(2000, 1, 3),
            2001: calendar.Date(2001, 1, 1),
            2002: calendar.Date(2001, 12, 31),
            2003: calendar.Date(2002, 12, 30),
            2004: calendar.Date(2003, 12, 29),
            2005: calendar.Date(2005, 1, 3),
        }

        for year, date in test_cases.items():
            asserts.equal(calendar.first_isodate(year), date)

    @testing.subjects(calendar.DAY, calendar.WEEK)
    def test_timedeltas(self):
        d1 = calendar.Date(2000, 1, 1)
        d2 = calendar.Date(2000, 1, 2)
        d3 = calendar.Date(2000, 1, 8)

        asserts.equal(d2, d1 + calendar.DAY)
        asserts.equal(d3, d1 + calendar.WEEK)


class TestYearMonth(testing.TestSuite):
    @testing.subjects(
        calendar.YearMonth.__add__,
        calendar.YearMonth.__iadd__,
        calendar.YearMonth.__sub__,
        calendar.YearMonth.__isub__,
    )
    def test_arithmetic(self):
        ym1 = calendar.YearMonth(2000, 1)
        ym2 = calendar.YearMonth(2000, 2)
        ym3 = calendar.YearMonth(2000, 3)

        asserts.equal(ym1 + 1, ym2)
        asserts.equal(ym1 + 2, ym3)
        asserts.equal(ym3 - 1, ym2)
        asserts.equal(ym3 - 2, ym1)

        asserts.equal(ym1 - ym2, -1)
        asserts.equal(ym2 - ym1, +1)
        asserts.equal(ym3 - ym1, +2)

    @testing.subjects(
        calendar.YearMonth.__ge__,
        calendar.YearMonth.__gt__,
        calendar.YearMonth.__le__,
        calendar.YearMonth.__lt__,
    )
    def test_comparisons(self):
        ym1 = calendar.YearMonth(2000, 1)
        ym2 = calendar.YearMonth(2000, 2)

        asserts.greater_equal(ym2, ym1)
        asserts.greater_equal(ym2, ym2)
        asserts.greater_than(ym2, ym1)

        asserts.less_equal(ym1, ym2)
        asserts.less_equal(ym1, ym1)
        asserts.less_than(ym1, ym2)

    @testing.subjects(
        calendar.YearMonth.__init__,
        calendar.YearMonth.current.__func__,
        calendar.YearMonth.from_date.__func__,
        calendar.YearMonth.from_integer.__func__,
        calendar.YearMonth.from_string.__func__,
    )
    def test_construction(self):
        YearMonth = calendar.YearMonth

        YM = YearMonth(2000, 1)

        asserts.equal(YM, YearMonth(12 * 2000))

        asserts.equal(YM, YearMonth.from_date(Date(2000, 1, 1)))
        asserts.equal(YM, YearMonth.from_date(Date(2000, 1, 2)))

        asserts.equal(YM, YearMonth.from_integer(200001))
        asserts.equal(YearMonth(0, 1), YearMonth.from_integer(1))
        asserts.equal(YearMonth(400, 12), YearMonth.from_integer(40012))
        asserts.raise_exception(ValueError, YearMonth.from_integer, -40012)

        asserts.equal(YM, YearMonth.from_string("200001"))
        asserts.equal(YearMonth(400, 12), YearMonth.from_string("040012"))
        asserts.raise_exception(ValueError, YearMonth.from_string, "40012")

    @testing.subjects(calendar.YearMonth.elapse)
    def test_elapse(self):
        ym1 = calendar.YearMonth(2000, 1)
        ym2 = calendar.YearMonth(2000, 2)
        ym3 = calendar.YearMonth(2000, 3)

        test_elapse_generic(calendar.YearMonth.elapse, ym1, ym2, ym3)

    @testing.subjects(
        calendar.YearMonth.__eq__,
        calendar.YearMonth.__hash__,
        calendar.YearMonth.__ne__,
    )
    def test_immutability(self):
        ym1 = calendar.YearMonth(2000, 1)
        ym2 = calendar.YearMonth(2000, 1)
        ym3 = calendar.YearMonth(2000, 2)

        with asserts.exception_context(AttributeError):
            ym1.value = 10

        asserts.not_identical(ym1, ym2)

        asserts.equal(ym1, ym2)
        asserts.not_equal(ym1, ym3)
        asserts.equal(hash(ym1), hash(ym2))
        asserts.not_equal(hash(ym1), hash(ym3))

        asserts.equal(ym1, 24000)
        asserts.equal(hash(ym1), hash(24000))
        asserts.equal(ym1, 24000.0)
        asserts.equal(hash(ym1), hash(24000.0))
        asserts.equal(ym1, 24000.0 + 0j)
        asserts.equal(hash(ym1), hash(24000.0 + 0j))

    @testing.subjects(calendar.YearMonth.__int__)
    def test_int(self):
        asserts.equal(200001, int(calendar.YearMonth(2000, 1)))

    @testing.subjects(calendar.YearMonth.is_valid_string)
    def test_is_valid_string(self):
        assert calendar.YearMonth.is_valid_string("202401")
        assert not calendar.YearMonth.is_valid_string("202415")

    @testing.subjects(calendar.YearMonth.__getitem__, calendar.YearMonth.__iter__)
    def test_iter(self):
        ym = calendar.YearMonth(2000, 1)
        d1 = Date(2000, 1, 1)
        d2 = Date(2000, 1, 31)

        asserts.equal(tuple(ym), tuple(calendar.elapse(d1, d2)))
        asserts.equal(ym[0], d1)
        asserts.equal(ym[-1], d2)

    @testing.subjects(calendar.YearMonth.__len__)
    def test_len(self):
        asserts.equal(28, len(calendar.YearMonth(2001, 2)))
        asserts.equal(29, len(calendar.YearMonth(2000, 2)))
        asserts.equal(30, len(calendar.YearMonth(2000, 4)))
        asserts.equal(31, len(calendar.YearMonth(2000, 1)))

    def test_month_wrapping(self):
        ym1 = calendar.YearMonth(2000, 1) - 1
        ym2 = calendar.YearMonth(2000, 12) + 1

        asserts.equal(ym1.year, 1999)
        asserts.equal(ym1.month, 12)

        asserts.equal(ym2.year, 2001)
        asserts.equal(ym2.month, 1)

        asserts.equal(ym1.month, (ym1 + 12).month)
        asserts.equal(ym1.year + 1, (ym1 + 12).year)

    @testing.subjects(calendar.YearMonth.__repr__)
    def test_repr(self):
        asserts.equal("YearMonth(2000, 1)", repr(calendar.YearMonth(2000, 1)))

    @testing.subjects(calendar.YearMonth.__str__)
    def test_str(self):
        asserts.equal("200001", str(calendar.YearMonth(2000, 1)))

    @testing.subjects(calendar.YearMonth.value)
    def test_value(self):
        ym = calendar.YearMonth(2000, 1)
        with asserts.exception_context(AttributeError):
            ym.value = 0

    @testing.subjects(
        calendar.YearMonth.month, calendar.YearMonth.year, calendar.YearMonth.yearmonth
    )
    def test_yearmonth(self):
        ym = calendar.YearMonth(2000, 1)
        asserts.equal(1, ym.month)
        asserts.equal(2000, ym.year)
        asserts.equal((2000, 1), ym.yearmonth)


class TestYearWeek(testing.TestSuite):
    @testing.subjects(
        calendar.YearWeek.__add__,
        calendar.YearWeek.__iadd__,
        calendar.YearWeek.__sub__,
        calendar.YearWeek.__isub__,
    )
    def test_arithmetic(self):
        ym1 = calendar.YearWeek(2000, 1)
        ym2 = calendar.YearWeek(2000, 2)
        ym3 = calendar.YearWeek(2000, 3)

        asserts.equal(ym1 + 1, ym2)
        asserts.equal(ym1 + 2, ym3)
        asserts.equal(ym3 - 1, ym2)
        asserts.equal(ym3 - 2, ym1)

        asserts.equal(ym1 - ym2, -1)
        asserts.equal(ym2 - ym1, +1)
        asserts.equal(ym3 - ym1, +2)

        yw1 = calendar.YearWeek(2000, 1) - 1
        yw2 = calendar.YearWeek(2000, 52) + 1

        asserts.equal(yw1.year, 1999)
        asserts.equal(yw1.week, 52)

        asserts.equal(yw2.year, 2001)
        asserts.equal(yw2.week, 1)

    @testing.subjects(
        calendar.YearWeek.__init__,
        calendar.YearWeek.from_date.__func__,
        calendar.YearWeek.from_string.__func__,
    )
    def test_construction(self):
        YearWeek = calendar.YearWeek

        for weekday in (expected := YearWeek.current()):
            asserts.equal(expected, YearWeek.from_date(weekday))

        YW = YearWeek(2000, 1)

        asserts.equal(YW, YearWeek.from_integer(200001))
        asserts.equal(YearWeek(1, 1), YearWeek.from_integer(101))
        asserts.equal(YearWeek(400, 12), YearWeek.from_integer(40012))
        asserts.raise_exception(ValueError, YearWeek.from_integer, -40012)

        asserts.equal(YW, YearWeek.from_string("200001"))
        asserts.equal(YearWeek(400, 12), YearWeek.from_string("040012"))
        asserts.raise_exception(ValueError, YearWeek.from_string, "200053")

    @testing.subjects(calendar.YearWeek.__getitem__)
    def test_getitem(self):
        yw = calendar.YearWeek.from_date(calendar.Date(2025, 3, 24))
        asserts.equal(calendar.Date(2025, 3, 24), yw[0])
        asserts.equal(calendar.Date(2025, 3, 25), yw[1])
        asserts.equal(calendar.Date(2025, 3, 26), yw[2])
        asserts.equal(calendar.Date(2025, 3, 27), yw[3])
        asserts.equal(calendar.Date(2025, 3, 28), yw[4])
        asserts.equal(calendar.Date(2025, 3, 29), yw[5])
        asserts.equal(calendar.Date(2025, 3, 30), yw[6])

    @testing.subjects(calendar.YearWeek.__int__)
    def test_int(self):
        asserts.equal(200001, int(calendar.YearWeek(2000, 1)))

    @testing.subjects(calendar.YearWeek.__len__)
    def test_len(self):
        asserts.equal(7, len(calendar.YearWeek(2000, 1)))
        asserts.equal(7, len(calendar.YearWeek(2000, 2)))
        asserts.equal(7, len(calendar.YearWeek(2000, 3)))
        asserts.equal(7, len(calendar.YearWeek(2000, 4)))

    @testing.subjects(calendar.YearWeek.range)
    def test_range(self):
        origin = calendar.YearWeek(2000, 6)

        expected = (origin, origin + 1, origin + 2)
        obtained = tuple(origin.range(3))
        asserts.equal(expected, obtained)

        expected = (origin, origin - 1, origin - 2)
        obtained = tuple(origin.range(-3))
        asserts.equal(expected, obtained)

        expected = (origin, origin + 2)
        obtained = tuple(origin.range(3, 2))
        asserts.equal(expected, obtained)

    @testing.subjects(calendar.YearWeek.__repr__)
    def test_repr(self):
        asserts.equal("YearWeek(2000, 1)", repr(calendar.YearWeek(2000, 1)))

    @testing.subjects(
        calendar.YearWeek.week, calendar.YearWeek.year, calendar.YearWeek.yearweek
    )
    def test_yearweek(self):
        ym = calendar.YearWeek(2000, 1)
        asserts.equal(1, ym.week)
        asserts.equal(2000, ym.year)
        asserts.equal((2000, 1), ym.yearweek)
