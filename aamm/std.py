import importlib.util
import os.path
import sys
from collections import deque
from math import ceil
from numbers import Number
from operator import ge, gt, le, lt
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
    r = ge if include_right else gt
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


def import_file(path: str | Path) -> ModuleType:
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
