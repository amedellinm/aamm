from aamm import graph, testing
from aamm.testing import asserts


class TestGraph(testing.TestSuite):
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

    @testing.subjects(graph.breadth_first)
    def test_breadth_first(self):
        expected = "abcde"
        obtained = "".join(graph.breadth_first("a", self.graph.get))
        asserts.equal(expected, obtained)

    @testing.subjects(graph.depth_first)
    def test_depth_first(self):
        expected = "abdec"
        obtained = "".join(graph.depth_first("a", self.graph.get))
        asserts.equal(expected, obtained)

    @testing.subjects(graph.breadth_first_paths)
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

    @testing.subjects(graph.depth_first_paths)
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
