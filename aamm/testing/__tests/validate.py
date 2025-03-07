from aamm.testing import TestSuite, asserts, main
from aamm.testing.validate import all_equal, between, sequences_equal


class TestStd(TestSuite):
    def test_all_equal(self):
        asserts.true(all_equal(tuple()))
        asserts.true(all_equal("a"))
        asserts.true(all_equal([1, 1]))
        asserts.false(all_equal({1, "1"}))

    def test_sequences_equal(self):
        asserts.true(sequences_equal((1, 2, 3), (1, 2, 3), (1, 2, 3)))
        asserts.true(sequences_equal((1, 2, 3), [1, 2, 3], (1, 2, 3)))
        asserts.false(sequences_equal((1, 2, 3), (1, 2, 4), (1, 2, 3)))
        asserts.false(sequences_equal((1, 2, 3), (2, 1, 3), (1, 2, 3)))

    def test_between(self):
        a, b = -4, 6

        asserts.false(between(-4, a, b, 0, 0))
        asserts.false(between(-4, a, b, 0, 1))
        asserts.true(between(-4, a, b, 1, 0))
        asserts.true(between(-4, a, b, 1, 1))

        asserts.true(between(5, a, b, 0, 0))
        asserts.true(between(5, a, b, 0, 1))
        asserts.true(between(5, a, b, 1, 0))
        asserts.true(between(5, a, b, 1, 1))

        asserts.false(between(6, a, b, 0, 0))
        asserts.true(between(6, a, b, 0, 1))
        asserts.false(between(6, a, b, 1, 0))
        asserts.true(between(6, a, b, 1, 1))


if __name__ == "__main__":
    main()
