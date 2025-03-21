from aamm import testing
from aamm.testing import asserts


class TestTestSuite(testing.TestSuite):
    @testing.subjects(asserts.assert_many)
    def test_assert_many(self):
        import sys

        if sys.version_info < (3, 11):
            return

        with asserts.exception_context(ExceptionGroup):
            with asserts.assert_many():
                asserts.equal(1, 0)
                asserts.true(False)

        with asserts.exception_context(AssertionError):
            with asserts.assert_many():
                asserts.equal(1, 0)

        with asserts.assert_many():
            pass

        with asserts.assert_many():
            asserts.equal(1, 1)

        with asserts.assert_many():
            asserts.equal(1, 1)
            asserts.equal(2, 2)

    @testing.subjects(asserts.between)
    def test_between(self):
        asserts.between(1, 1, 3, 1, 0)
        asserts.between(1, 1, 3, 1, 1)
        asserts.between(2, 1, 3, 0, 0)
        asserts.between(2, 1, 3, 0, 1)
        asserts.between(2, 1, 3, 1, 0)
        asserts.between(2, 1, 3, 1, 1)
        asserts.between(3, 1, 3, 0, 1)
        asserts.between(3, 1, 3, 1, 1)

        with asserts.exception_context(AssertionError):
            asserts.between(1, 1, 3, 0, 0)
            asserts.between(1, 1, 3, 0, 1)
            asserts.between(3, 1, 3, 0, 0)
            asserts.between(3, 1, 3, 1, 0)

    @testing.subjects(asserts.contain)
    def test_contain(self):
        container = ("a", "b")
        asserts.contain(container, "a")
        asserts.contain(container, "b")

        with asserts.exception_context(AssertionError):
            asserts.contain(container, "c")

    @testing.subjects(asserts.equal)
    def test_equal(self):
        asserts.equal(1, 1.0)

        with asserts.exception_context(AssertionError):
            asserts.equal(1, 2)

    @testing.subjects(asserts.exception_context)
    def test_exception_context(self):
        with asserts.exception_context(AssertionError):
            assert False

    @testing.subjects(asserts.false)
    def test_false(self):
        asserts.false(False)

        with asserts.exception_context(AssertionError):
            asserts.false(True)

    @testing.subjects(asserts.greater_equal)
    def test_greater_equal(self):
        asserts.greater_equal(2, 1)
        asserts.greater_equal(2, 2)

        with asserts.exception_context(AssertionError):
            asserts.greater_equal(2, 3)

    @testing.subjects(asserts.greater_than)
    def test_greater_than(self):
        asserts.greater_than(2, 1)

        with asserts.exception_context(AssertionError):
            asserts.greater_than(2, 2)
            asserts.greater_than(2, 3)

    @testing.subjects(asserts.identical)
    def test_identical(self):
        a = [1, 2, 3]
        b = [1, 2, 3]
        c = a
        asserts.identical(a, c)

        with asserts.exception_context(AssertionError):
            asserts.identical(a, b)

    @testing.subjects(asserts.less_equal)
    def test_less_equal(self):
        asserts.less_equal(1, 2)
        asserts.less_equal(1, 1)

        with asserts.exception_context(AssertionError):
            asserts.less_equal(1, 0)

    @testing.subjects(asserts.less_than)
    def test_less_than(self):
        asserts.less_than(1, 2)

        with asserts.exception_context(AssertionError):
            asserts.less_than(1, 1)
            asserts.less_than(1, 0)

    @testing.subjects(asserts.not_contain)
    def test_not_contain(self):
        asserts.not_contain((), 0)

        with asserts.exception_context(AssertionError):
            asserts.not_contain((0,), 0)

    @testing.subjects(asserts.not_equal)
    def test_not_equal(self):
        asserts.not_equal(1, 0)

        with asserts.exception_context(AssertionError):
            asserts.not_equal(1, 1)

    @testing.subjects(asserts.not_identical)
    def test_not_identical(self):
        asserts.not_identical(1, 0)
        a = b = []

        with asserts.exception_context(AssertionError):
            asserts.not_identical(a, b)

    @testing.subjects(asserts.raise_exception)
    def test_raise_exception(self):
        asserts.raise_exception(TypeError, lambda *_: 1 + "1")

        with asserts.exception_context(AssertionError):
            asserts.raise_exception(TypeError, lambda *_: 1 + 1)

    @testing.subjects(asserts.true)
    def test_true(self):
        asserts.true(True)

        with asserts.exception_context(AssertionError):
            asserts.true(None)
