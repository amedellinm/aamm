from collections import deque
from collections.abc import Callable, Iterator
from typing import Any


def breadth_first(root: Any, expand: Callable[[Any], Iterator[Any]]) -> Iterator[Any]:
    """Traverse a graph from `root` using breadth-first."""
    queue = deque([root])
    while queue:
        yield (node := queue.popleft())
        queue.extend(expand(node))


def depth_first(root: Any, expand: Callable[[Any], Iterator[Any]]) -> Iterator[Any]:
    """Traverse a graph from `root` using depth-first."""
    queue = [root]
    while queue:
        yield (node := queue.pop())
        queue.extend(reversed(expand(node)))
