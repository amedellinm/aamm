from aamm import graph
from aamm.testing import TestSuite, asserts


class TestGraph(TestSuite):

    @classmethod
    def initialize(cls):
        cls.graph = {
            "a": ["b", "c"],
            "b": ["d", "e"],
            "c": [],
            "d": ["a"],
            "e": [],
        }

        #       - a
        #     /  / \
        #    /  b   c
        #    \ / \
        #     d   e

    def test_breadth_first(self):
        expected = "abcde"
        obtained = "".join(graph.breadth_first("a", self.graph.get))
        asserts.equal(expected, obtained)

    def test_depth_first(self):
        expected = "abdec"
        obtained = "".join(graph.depth_first("a", self.graph.get))
        asserts.equal(expected, obtained)

    def test_breadth_first_paths(self):
        expected = (
            ["a"],
            ["a", "b"],
            ["a", "c"],
            ["a", "b", "d"],
            ["a", "b", "e"],
        )
        obtained = tuple(graph.breadth_first_paths("a", self.graph.get))
        asserts.equal(expected, obtained)

    def test_depth_first_paths(self):
        expected = (
            ["a"],
            ["a", "b"],
            ["a", "b", "d"],
            ["a", "b", "e"],
            ["a", "c"],
        )
        obtained = tuple(graph.depth_first_paths("a", self.graph.get))
        asserts.equal(expected, obtained)
