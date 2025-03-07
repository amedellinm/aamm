from collections.abc import Iterable, Sequence
from operator import le, lt


def all_equal(iterable: Iterable) -> bool:
    """Test equality between all elements of a sequence."""
    iterator = iter(iterable)
    first = next(iterator, ...)
    return all(first == other for other in iterator)


def between(
    value, lower, upper, include_lower: bool = True, include_upper: bool = True
) -> bool:
    """Check `value` is between `lower` and `upper`."""
    l = le if include_lower else lt
    r = le if include_upper else lt
    return l(lower, value) and r(value, upper)


def sequences_equal(*sequences: tuple[Sequence]) -> bool:
    """Test equality between the nth element of all sequences, for all elements."""
    return all_equal(map(len, sequences)) and all(map(all_equal, zip(*sequences)))
