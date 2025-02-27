from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Iterator, Sequence


def cap_iter(iterable: Iterable, n: int) -> Iterator:
    """Cap an iterable to `n` iterations."""
    for i, _ in zip(iterable, range(n)):
        yield i


def group_by(
    data: Iterable[tuple[Hashable]],
    keys: int | Sequence[int] = 0,
    values: int | Sequence[int] | None = None,
) -> defaultdict:
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


def skip_iter(iterable: Iterable, n: int = 1) -> Iterator:
    """Skip `n` iterations of `iterable`."""
    iterable = iter(iterable)
    for _ in range(n):
        next(iterable)
    return iterable


def split_iter(iterable: Iterable, condition: Callable) -> tuple[list, list]:
    """Like filter but return a `tuple` of two `list`s: (true_group, false_group)."""

    true_group = []
    false_group = []

    for i in iterable:
        if condition(i):
            true_group.append(i)
        else:
            false_group.append(i)

    return true_group, false_group
