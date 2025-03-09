from collections import deque
from collections.abc import Callable, Iterator
from typing import Any


def breadth_first(root: Any, expand: Callable[[Any], Iterator[Any]]) -> Iterator[Any]:
    """Traverse a graph from `root` using breadth-first."""
    queue = deque([root])
    known = set()

    while queue:
        node = queue.popleft()

        if node in known:
            continue
        known.add(node)

        yield node

        queue.extend(expand(node))


def breadth_first_paths(
    root: Any, expand: Callable[[Any], Iterator[Any]], sentinel: Any = ...
) -> Iterator[list[Any]]:
    path = []
    queue = deque([root])
    known = set()

    yield [root]

    while queue:
        node = queue.popleft()

        if node is sentinel:
            path.pop()
            continue
        known.add(node)

        path.append(node)
        nodes = tuple(n for n in expand(node) if n not in known)
        for n in nodes:
            yield path + [n]

        queue.extend(nodes)
        queue.append(sentinel)


def depth_first(root: Any, expand: Callable[[Any], Iterator[Any]]) -> Iterator[Any]:
    """Traverse a graph from `root` using depth-first."""
    queue = [root]
    known = set()
    while queue:
        node = queue.pop()

        if node in known:
            continue
        known.add(node)

        yield node

        queue.extend(reversed(expand(node)))


def depth_first_paths(
    root: Any, expand: Callable[[Any], Iterator[Any]], sentinel: Any = ...
) -> Iterator[list[Any]]:
    path = []
    queue = [root]
    known = set()

    while queue:
        node = queue.pop()

        if node is sentinel:
            path.pop()
            continue
        known.add(node)

        path.append(node)
        yield path.copy()

        nodes = tuple(n for n in expand(node) if n not in known)
        queue.append(sentinel)
        queue.extend(reversed(nodes))
