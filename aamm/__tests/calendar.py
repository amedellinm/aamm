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
    def test_elapse(self):
        d1 = Date(2000, 1, 1)
        d2 = Date(2000, 1, 2)
        d3 = Date(2000, 1, 3)

        test_elapse_generic(calendar.elapse, d1, d2, d3)

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


class TestYearMonth(testing.TestSuite):
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

    def test_elapse(self):
        ym1 = calendar.YearMonth(2000, 1)
        ym2 = calendar.YearMonth(2000, 2)
        ym3 = calendar.YearMonth(2000, 3)

        test_elapse_generic(calendar.YearMonth.elapse, ym1, ym2, ym3)

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

    def test_iter(self):
        ym = calendar.YearMonth(2000, 1)
        d1 = Date(2000, 1, 1)
        d2 = Date(2000, 1, 31)

        asserts.equal(tuple(ym), tuple(calendar.elapse(d1, d2)))
        asserts.equal(ym[0], d1)
        asserts.equal(ym[-1], d2)

    def test_month_wrapping(self):
        ym1 = calendar.YearMonth(2000, 1) - 1
        ym2 = calendar.YearMonth(2000, 12) + 1

        asserts.equal(ym1.year, 1999)
        asserts.equal(ym1.month, 12)

        asserts.equal(ym2.year, 2001)
        asserts.equal(ym2.month, 1)

        asserts.equal(ym1.month, (ym1 + 12).month)
        asserts.equal(ym1.year + 1, (ym1 + 12).year)


class TestYearWeek(testing.TestSuite):
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

    def test_elapse(self):
        ym1 = calendar.YearWeek(2000, 1)
        ym2 = calendar.YearWeek(2000, 2)
        ym3 = calendar.YearWeek(2000, 3)

        test_elapse_generic(calendar.YearWeek.elapse, ym1, ym2, ym3)

    def test_immutability(self):
        ym1 = calendar.YearWeek(2000, 1)
        ym2 = calendar.YearWeek(2000, 1)
        ym3 = calendar.YearWeek(2000, 2)

        with asserts.exception_context(AttributeError):
            ym1.value = 10

        asserts.not_identical(ym1, ym2)

        asserts.equal(ym1, ym2)
        asserts.not_equal(ym1, ym3)
        asserts.equal(hash(ym1), hash(ym2))
        asserts.not_equal(hash(ym1), hash(ym3))

        asserts.equal(ym1, 104303)
        asserts.equal(hash(ym1), hash(104303))
        asserts.equal(ym1, 104303.0)
        asserts.equal(hash(ym1), hash(104303.0))

    def test_iter(self):
        ym = calendar.YearWeek(2000, 1)
        asserts.equal(tuple(ym), tuple(calendar.elapse(ym[0], ym[-1])))

    def test_week_wrapping(self):
        yw1 = calendar.YearWeek(2000, 1) - 1
        yw2 = calendar.YearWeek(2000, 52) + 1

        asserts.equal(yw1.year, 1999)
        asserts.equal(yw1.week, 52)

        asserts.equal(yw2.year, 2001)
        asserts.equal(yw2.week, 1)
