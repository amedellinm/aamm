from aamm.iterable import cap_iter, group_by, hinted_sort, skip_iter, split_iter
from aamm.testing import TestSuite, asserts, main


class TestIterable(TestSuite):
    def test_cap_iter(self):
        def generator():
            while True:
                yield

        for i in range(20):
            asserts.equal(sum(1 for _ in cap_iter(generator(), i)), i)

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
