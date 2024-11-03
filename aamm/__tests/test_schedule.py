from datetime import date as Date

from aamm import schedule, testing
from aamm.testing import asserts


def test_elapse_generic(elapse, x1, x2, x3):
    asserts.equal(tuple(elapse(x1, x3)), (x1, x2, x3))
    asserts.equal(tuple(elapse(x3, x1)), (x3, x2, x1))

    asserts.equal(tuple(elapse(x1, x3, 2)), (x1, x3))
    asserts.equal(tuple(elapse(x3, x1, 2)), (x3, x1))
    asserts.equal(tuple(elapse(x3, x1, -2)), (x3, x1))


class TestSchedule(testing.TestSuite):
    def test_elapse(self):
        d1 = Date(2000, 1, 1)
        d2 = Date(2000, 1, 2)
        d3 = Date(2000, 1, 3)

        test_elapse_generic(schedule.elapse, d1, d2, d3)

    def test_find_weekday(self):
        d1 = Date(2000, 1, 1)
        d2 = Date(2000, 1, 2)
        d3 = Date(2000, 1, 8)

        asserts.equal(schedule.find_weekday(d1, d1.weekday()), d3)

        asserts.equal(schedule.find_weekday(d1, d2.weekday()), d2)
        asserts.equal(schedule.find_weekday(d1, d2.weekday(), 1, True), d2)

        asserts.equal(schedule.find_weekday(d2, d1.weekday()), d3)
        asserts.equal(schedule.find_weekday(d2, d1.weekday(), -1), d1)
        asserts.equal(schedule.find_weekday(d2, d1.weekday(), -1, True), d1)

        asserts.equal(schedule.find_weekday(d1, d1.weekday(), 1, True), d1)
        asserts.equal(schedule.find_weekday(d3, d3.weekday(), -1), d1)
        asserts.equal(schedule.find_weekday(d3, d3.weekday(), -1, True), d3)

        asserts.raise_exception(ValueError, schedule.find_weekday, d1, d1.weekday(), 0)


class TestYearMonth(testing.TestSuite):
    def test_arithmetic(self):
        ym1 = schedule.YearMonth(2000, 1)
        ym2 = schedule.YearMonth(2000, 2)
        ym3 = schedule.YearMonth(2000, 3)

        asserts.equal(ym1 + 1, ym2)
        asserts.equal(ym1 + 2, ym3)
        asserts.equal(ym3 - 1, ym2)
        asserts.equal(ym3 - 2, ym1)

        asserts.equal(ym1 - ym2, -1)
        asserts.equal(ym2 - ym1, +1)
        asserts.equal(ym3 - ym1, +2)

    def test_construction(self):
        YearMonth = schedule.YearMonth

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
        ym1 = schedule.YearMonth(2000, 1)
        ym2 = schedule.YearMonth(2000, 2)
        ym3 = schedule.YearMonth(2000, 3)

        test_elapse_generic(schedule.YearMonth.elapse, ym1, ym2, ym3)

    def test_immutability(self):
        ym1 = schedule.YearMonth(2000, 1)
        ym2 = schedule.YearMonth(2000, 1)
        ym3 = schedule.YearMonth(2000, 2)

        with asserts.exception_context(AttributeError):
            ym1.value = 10

        asserts.false(ym1 is ym2)

        asserts.true(ym1 == ym2)
        asserts.false(ym1 == ym3)
        asserts.true(hash(ym1) == hash(ym2))
        asserts.false(hash(ym1) == hash(ym3))

        asserts.true(ym1 == 24000)
        asserts.true(hash(ym1) == hash(24000))
        asserts.true(ym1 == 24000.0)
        asserts.true(hash(ym1) == hash(24000.0))
        asserts.true(ym1 == 24000.0 + 0j)
        asserts.true(hash(ym1) == hash(24000.0 + 0j))

    def test_iter(self):
        ym = schedule.YearMonth(2000, 1)
        d1 = Date(2000, 1, 1)
        d2 = Date(2000, 1, 31)

        asserts.equal(tuple(ym), tuple(schedule.elapse(d1, d2)))
        asserts.equal(ym[0], d1)
        asserts.equal(ym[-1], d2)

    def test_month_wrapping(self):
        ym1 = schedule.YearMonth(2000, 1) - 1
        ym2 = schedule.YearMonth(2000, 12) + 1

        asserts.equal(ym1.year, 1999)
        asserts.equal(ym1.month, 12)

        asserts.equal(ym2.year, 2001)
        asserts.equal(ym2.month, 1)

        asserts.equal(ym1.month, (ym1 + 12).month)
        asserts.equal(ym1.year + 1, (ym1 + 12).year)


if __name__ == "__main__":
    testing.main()
