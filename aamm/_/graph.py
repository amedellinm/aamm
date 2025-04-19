from collections import deque
from collections.abc import Callable, Hashable, Iterator
from typing import Any, TypeVar

T = TypeVar("T", bound=Hashable)


def breadth_first(root: T, expand: Callable[[T], Iterator[T]]) -> Iterator[T]:
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
    root: T, expand: Callable[[T], Iterator[T]], sentinel: Any = ...
) -> Iterator[list[T]]:
    """Like `breadth_first` but yield paths instead of single nodes."""
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


def depth_first(root: T, expand: Callable[[T], Iterator[T]]) -> Iterator[T]:
    """Traverse a graph from `root` using depth-first."""
    queue = [root]
    known = set()
    while queue:
        node = queue.pop()

        if node in known:
            continue
        known.add(node)

        yield node

        queue.extend(reversed(tuple(expand(node))))


def depth_first_paths(
    root: T,
    expand: Callable[[T], Iterator[T]],
    sentinel: Any = ...,
) -> Iterator[list[T]]:
    """Like `depth_first` but yield paths instead of single nodes."""
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
