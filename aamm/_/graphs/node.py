from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable, Iterator


class Node(ABC):
    def breadth_first(self) -> Iterator:
        """Traverses a graph from `self` using breadth-first."""
        queue = deque([self])
        while queue:
            yield (node := queue.popleft())
            queue.extend(node.expand())

    def depth_first(self) -> Iterator:
        """Traverses a graph from `self` using depth-first."""
        queue = [self]
        while queue:
            yield (node := queue.pop())
            queue.extend(reversed(node.expand()))

    @abstractmethod
    def expand(self) -> Iterable:
        pass
