import importlib.util
import os.path
import sys
from collections import defaultdict, deque
from math import ceil
from numbers import Number
from operator import le, lt
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Generator, Iterable, Iterator, Sequence

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def all_equal(iterable: Iterable) -> bool:
    """Test equality between all elements of a sequence."""
    first = next(others := iter(iterable))
    for other in others:
        if first != other:
            return False
    return True


def are_sequences_equal(*sequences: tuple[Sequence]) -> bool:
    """Test equality between the nth element of all sequences, for all elements."""
    if not all_equal(map(len, sequences)):
        return False
    return all(map(all_equal, zip(sequences)))


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

    def fetch_one(row: tuple, index: int):
        return row[index]

    def fetch_many(row: tuple, index: tuple[int]):
        return tuple(row[i] for i in index)

    grouped_data = defaultdict(list)
    data = iter(data)

    try:
        row = next(data)
    except StopIteration:
        return {}

    if values is None:
        if isinstance(keys, int):
            values = tuple(i for i in range(len(row)) if i != keys)
            fetch_keys = fetch_one
        else:
            fetch_keys = fetch_many
            values = tuple(i for i in range(len(row)) if i not in keys)
    elif isinstance(values, int):
        values = (values,)

    fetch_values = fetch_one if len(values) == 1 else fetch_many

    grouped_data[fetch_keys(row, keys)].append(fetch_many(row, values))

    for row in data:
        grouped_data[fetch_keys(row, keys)].append(fetch_values(row, values))

    return grouped_data


def import_path(path: str | Path) -> ModuleType:
    """Imports a Python module (.py) from a path"""
    module_name, _ = os.path.splitext(os.path.basename(path))
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def index(sequence: Sequence, item: Any) -> int:
    """Get `item`'s index in `sequence` if it exists, else return `len(sequence)`."""
    for n, i in enumerate(sequence):
        if i == item:
            return n
    return n + 1


def is_divisible(numerator: int, denominator: int) -> bool:
    """Returns whether numerator is divisible by denominator.."""
    return not (numerator % denominator)


def iterbits(array: bytearray) -> Generator:
    """Yields all bits from a `bytearray` in order."""
    for byte in array:
        for n in range(7, -1, -1):
            yield bool(byte & 2**n)


def loop(iterable: Iterable, n: int | None = None) -> Generator:
    """Iterates over `iterable` in a cyclic fashion `n` times or indefinitely."""
    if n is None:
        while True:
            yield from iterable
    else:
        for _ in range(n):
            yield from iterable


def mod_complement(numerator: int, denominator: int) -> int:
    """Difference between `numerator` and the next multiple of `denominator`"""
    mod = numerator % denominator
    return denominator - mod if mod else 0


def qualname(obj: Any) -> str:
    """Returns the qualname of an object's type"""
    return type(obj).__qualname__


def raise_many(*exceptions: tuple[Exception | None], message: str = "") -> None:
    exceptions = tuple(e for e in exceptions if e is not None)
    match len(exceptions):
        case 0:
            return
        case 1:
            raise exceptions[0]
        case _:
            raise ExceptionGroup(message, exceptions)


def sign(number: Number, zero_case: str = 0) -> int:
    return zero_case if number == 0 else 1 if number > 0 else -1


def sign_string(number: Number, zero_case: str = "") -> str:
    return zero_case if number == 0 else "+" if number > 0 else "-"


def skip_iter(iterable: Iterable, n: int = 1) -> Iterator:
    """Skips `n` iterations of `iterable`."""
    iterable = iter(iterable)
    for _ in range(n):
        next(iterable)
    return iterable
