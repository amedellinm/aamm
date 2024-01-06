import importlib.util
import os.path
import sys
from collections import deque
from contextlib import contextmanager
from functools import wraps
from math import ceil
from pathlib import Path
from types import ModuleType
from typing import (
    Any,
    Callable,
    ContextManager,
    Generator,
    Iterable,
    Literal,
    Sequence,
    TextIO,
)

from aamm.formats.exceptions import attribute_error

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def all_equal(it: Iterable) -> bool:
    """Test equality between all elements of a sequence."""
    return len(frozenset(it)) == 1


def are_sequences_equal(*sequences: Iterable[Sequence]) -> bool:
    """Test equality between the nth element of all sequences, for all elements."""
    sequences = tuple(sequences)
    if not all_equal(map(len, sequences)):
        return False
    return all(map(all_equal, zip(sequences)))


def cap_iter(it: Iterable, n: int = None) -> Generator:
    """Caps an iterator to `n` iterations."""
    if n is None:
        yield from it
        return
    for item, _ in zip(it, range(n)):
        yield item


@contextmanager
def capture_stdout(file_path: str | Path, mode: str = "a") -> ContextManager[TextIO]:
    """Temporarily redirects the stdout traffic to `file_path`."""
    stdout = sys.stdout
    with open(file_path, mode) as file:
        sys.stdout = file
        try:
            yield file
        finally:
            sys.stdout = stdout


def breadth_first(root, expand: Callable) -> Generator:
    """Explores a tree from a root node using the breadth-first strategy."""
    queue = deque([root])
    while queue:
        yield (node := queue.popleft())
        queue.extend(expand(node))


def byte_length(integer: int) -> int:
    """Computes the minimum number of bytes needed to hold an unsigned integer."""
    return ceil(integer.bit_length() / 8) or 1


def deprecation(msg: str) -> Callable:
    """Prints a deprecation warning message before every call."""

    def decorator(function: Callable) -> Callable:
        @wraps
        def decorated(*args, **kwargs):
            print(msg)
            return function(*args, **kwargs)

        return decorated

    if isinstance(msg, Callable):
        f = decorator(msg)
        msg = f"Function {function.__name__} is scheduled for deprecation"
        return f

    return decorator


def depth_first(root, expand: Callable) -> Generator:
    """Explores a tree from a root node using the depth-first strategy."""
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


def index(sequence: Sequence, item: Any) -> int | None:
    """Returns the index to find `item` inside `sequence`."""
    for n, i in enumerate(sequence):
        if i == item:
            return n


def iterbits(array: bytearray) -> Generator:
    """Yields all bits from a `bytearray` in order."""
    for byte in array:
        for n in range(7, -1, -1):
            yield bool(byte & 2**n)


def loop(it: Iterable, n: int = None) -> Generator:
    """Iterates over `it` in a circular fashion `n` times or indefinitely."""
    if n is None:
        while True:
            yield from it
    else:
        for _ in range(n):
            yield from it


def mod_complement(numerator: int, denominator: int) -> int:
    """Difference between `numerator` and the next multiple of `denominator`"""
    mod = numerator % denominator
    return denominator - mod if mod else 0


def reversed_enumerate(it: Iterable, start: int = ...) -> Generator:
    """The `enumerate` function but yields `(item, n)` instead of `(n, item)`."""
    return ((item, n) for n, item in enumerate(it, start))


def skip_iter(it: Iterable, n: int = 0) -> Iterable:
    """Skips `n` iterations of `it`."""
    it = iter(it)
    for _ in range(n):
        next(it)
    return it


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


class ReadOnlyProperty:
    """Descriptor that allows one single write operation then becomes read-only."""

    def __set_name__(self, _, name):
        self.display_name = name
        self.private_name = "_" + name

    def __get__(self, obj, objtype: type = None):
        if obj is None:
            raise AttributeError(attribute_error(objtype, self.display_name))
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if hasattr(obj, self.private_name):
            raise AttributeError(f"Property '{self.display_name}' is read-only")
        setattr(obj, self.private_name, value)


def ConstantBooleanOperations(boolean_methods: dict[str, bool]) -> object:
    """
    Description
    -----------
    Creates an object whose boolean operation results are fixed.
    >>> "anything" in ConstantBooleanOperations({"__contains__": True})
    True

    """

    def return_true(*_) -> Literal[True]:
        return True

    def return_false(*_) -> Literal[False]:
        return False

    ConstantBooleanOperations = type("ConstantBooleanOperations", (), {})

    for method_name, boolean in boolean_methods.items():
        setattr(
            ConstantBooleanOperations,
            method_name,
            return_true if boolean else return_false,
        )

    return ConstantBooleanOperations()
