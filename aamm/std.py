from collections import defaultdict, deque
from math import ceil
from numbers import Number
from operator import le, lt
from typing import Any, Callable, Generator, Iterable, Iterator, Sequence

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def all_equal(iterable: Iterable) -> bool:
    """Test equality between all elements of a sequence."""
    try:
        first = next(iterator := iter(iterable))
    except StopIteration:
        return True
    return all(first == other for other in iterator)


def between(
    value, left, right, include_left: bool = True, include_right: bool = True
) -> bool:
    """Check `value` is between `left` and `right`."""
    l = le if include_left else lt
    r = le if include_right else lt
    return l(left, value) and r(value, right)


def breadth_first(root: Any, expand: Callable) -> Generator:
    """Traverses a graph from a root node using depth-first.."""
    queue = deque([root])
    while queue:
        yield (node := queue.popleft())
        queue.extend(expand(node))


def byte_length(integer: int) -> int:
    """Computes the minimum number of bytes needed to hold an integer."""
    bits = integer.bit_length() + (integer < 0)
    return ceil(bits / 8) or 1


def cap_iter(iterable: Iterable, n: int | None = None) -> Generator:
    """Caps an iterator to `n` iterations."""
    if n is None:
        yield from iterable
        return
    for i, _ in zip(iterable, range(n)):
        yield i


def depth_first(root: Any, expand: Callable) -> Generator:
    """Traverses a graph from a root node using depth-first.."""
    queue = [root]
    while queue:
        yield (node := queue.pop())
        queue.extend(reversed(expand(node)))


def digits(integer: int) -> int:
    """Returns the number of digits in a given int."""
    return len(str(abs(integer)))


def group_by(
    data: Iterable[tuple],
    keys: int | Sequence[int] = 0,
    values: int | Sequence[int] | None = None,
) -> dict:
    """Group data based on the indices given as `keys` and `values`."""

    def fetch_one(row: tuple, index: int):
        return row[index]

    def fetch_many(row: tuple, index: tuple[int]):
        return tuple(row[i] for i in index)

    data = iter(data)

    try:
        row = next(data)
    except StopIteration:
        return {}

    grouped_data = defaultdict(list)

    if isinstance(keys, int):
        keys = (keys,)
    if isinstance(values, int):
        values = (values,)
    elif values is None:
        values = tuple(i for i in range(len(row)) if i not in keys)

    if len(keys) == 1:
        keys = keys[0]
        fetch_keys = fetch_one
    else:
        fetch_keys = fetch_many

    if len(values) == 1:
        values = values[0]
        fetch_values = fetch_one
    else:
        fetch_values = fetch_many

    grouped_data[fetch_keys(row, keys)].append(fetch_values(row, values))

    for row in data:
        grouped_data[fetch_keys(row, keys)].append(fetch_values(row, values))

    return grouped_data


def hinted_sort(
    sequence: Iterable,
    hint: Sequence,
    key: Callable | None = None,
    reverse: bool = False,
) -> list:
    """Sort `sequence` giving special treatement to the elements in `hint`."""
    hint = {element: index for index, element in enumerate(hint)}
    default = len(hint)

    if key is None:
        key = lambda x: x

    def hinted_key(value):
        return (hint.get(value, default), key(value))

    return sorted(sequence, key=hinted_key, reverse=reverse)


def index(sequence: Sequence, item: Any) -> int:
    """Get `item`'s index in `sequence` if it exists, else return `len(sequence)`."""
    for n, i in enumerate(sequence):
        if i == item:
            return n
    return n + 1


def loop(iterable: Iterable, n: int | None = None) -> Generator:
    """Iterates over `iterable` in a cyclic fashion `n` times or indefinitely."""
    if n is None:
        while True:
            yield from iterable
    else:
        for _ in range(n):
            yield from iterable


def qualname(obj: Any) -> str:
    """Returns the qualname of an object's type"""
    return type(obj).__qualname__


def sequences_equal(*sequences: tuple[Sequence]) -> bool:
    """Test equality between the nth element of all sequences, for all elements."""
    if not all_equal(map(len, sequences)):
        return False
    return all(map(all_equal, zip(sequences)))


def sign(number: Number, negative: Any = -1, zero: Any = 0, positive: Any = 1) -> Any:
    """return `negative`, `zero` or `positive` base on the sign of `number`."""
    return zero if number == 0 else positive if number > 0 else negative


def skip_iter(iterable: Iterable, n: int = 1) -> Iterator:
    """Skips `n` iterations of `iterable`."""
    iterable = iter(iterable)
    for _ in range(n):
        next(iterable)
    return iterable


def split_iter(iterable: Iterable, condition: Callable):
    """Split `iterable` in two lists using a boolean-returning callable as key."""
    true_group = []
    false_group = []

    for i in iterable:
        if condition(i):
            true_group.append(i)
        else:
            false_group.append(i)

    return true_group, false_group
