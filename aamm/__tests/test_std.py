from aamm.std import (
    all_equal,
    between,
    breadth_first,
    byte_length,
    cap_iter,
    depth_first,
    digits,
    group_by,
    hinted_sort,
    index,
    loop,
    qualname,
    sequences_equal,
    sign,
    skip_iter,
    split_iter,
)
from aamm.testing import TestSuite, asserts, main


class TestStd(TestSuite):
    def test_all_equal(self):
        asserts.true(all_equal(tuple()))
        asserts.true(all_equal("a"))
        asserts.true(all_equal([1, 1]))
        asserts.false(all_equal({1, "1"}))

    def test_are_sequences_equal(self):
        asserts.true(sequences_equal((1, 2, 3), (1, 2, 3), (1, 2, 3)))
        asserts.true(sequences_equal((1, 2, 3), [1, 2, 3], (1, 2, 3)))
        asserts.true(sequences_equal((1, 2, 3), (1, 2, 4), (1, 2, 3)))
        asserts.true(sequences_equal((1, 2, 3), (2, 1, 3), (1, 2, 3)))

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

    def test_breadth_first(self):
        def expand(node):
            return graph.get(node, [])

        graph = {
            0: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
        }

        asserts.equal(tuple(breadth_first(0, expand)), tuple(range(0, 10)))

    def test_byte_length(self):
        for i in range(10):
            value = 2 ** (8 * i)
            asserts.equal(byte_length(value), i + 1)
            asserts.equal(byte_length(1 - value), i + 1)

    def test_cap_iter(self):
        asserts.equal(sum(1 for _ in cap_iter(6 * [0])), 6)

        def generator():
            while True:
                yield

        for i in range(20):
            asserts.equal(sum(1 for _ in cap_iter(generator(), i)), i)

    def test_depth_first(self):
        def expand(node):
            return graph.get(node, [])

        graph = {
            0: [1, 2, 6],
            2: [3, 4, 5],
            6: [7, 8, 9],
        }

        asserts.equal(tuple(depth_first(0, expand)), tuple(range(0, 10)))

    def test_digits(self):
        for i in range(10):
            asserts.equal(digits(+(10**i)), i + 1)
            asserts.equal(digits(-(10**i)), i + 1)

    def test_group_by(self):
        data = [
            ("A", 1, "a"),
            ("A", 2, "a"),
            ("B", 3, "a"),
            ("C", 4, "b"),
        ]

        expected = {"A": [(1, "a"), (2, "a")], "B": [(3, "a")], "C": [(4, "b")]}
        asserts.equal(dict(group_by(data)), expected)

        expected = {("A", "a"): [1, 2], ("B", "a"): [3], ("C", "b"): [4]}
        asserts.equal(dict(group_by(data, [0, 2])), expected)

        expected = {"A": [1, 2], "B": [3], "C": [4]}
        asserts.equal(dict(group_by(data, values=[1])), expected)

    def test_hinted_sort(self):
        sequence = [2, 1, 6, 2]
        asserts.equal(hinted_sort(sequence, []), [1, 2, 2, 6])
        asserts.equal(hinted_sort(sequence, [6]), [6, 1, 2, 2])
        asserts.equal(hinted_sort(sequence, [1], None, 1), [6, 2, 2, 1])
        asserts.equal(hinted_sort(sequence, [2], None, 1), [6, 1, 2, 2])
        asserts.equal(hinted_sort(sequence, [2, 6], None, 1), [1, 6, 2, 2])

    def test_index(self):
        for i, char in enumerate(seq := "abcdefg"):
            asserts.equal(index(seq, char), i)
        asserts.equal(index(seq, "z"), len(seq))

    def test_loop(self):
        iterable = [1, 2]
        asserts.equal(list(loop(iterable, 2)), 2 * iterable)
        asserts.equal(len(list(zip(range(3), loop(iterable)))), 3)

    def test_sign(self):
        for i in (-1, 0, 1):
            asserts.equal(sign(i), i)

    def test_skip_iter(self):
        asserts.equal(tuple(skip_iter(range(10), 5)), tuple(range(5, 10)))

    def test_split_iter(self):
        numbers = range(1, 21)
        odds = list(range(1, 21, 2))
        evens = list(range(2, 21, 2))

        true_group, false_group = split_iter(numbers, lambda number: number % 2)

        asserts.equal(odds, true_group)
        asserts.equal(evens, false_group)


if __name__ == "__main__":
    main()
