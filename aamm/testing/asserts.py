from collections.abc import Container
from contextlib import contextmanager
from typing import Any

from aamm.std import between as std_between

_exceptions = []
_throw = True


@contextmanager
def assert_many():
    global _exceptions, _throw
    _throw = False
    try:
        yield
        if len(_exceptions) == 1:
            raise _exceptions[0]
        if len(_exceptions) > 1:
            raise ExceptionGroup("assertion error(s)", _exceptions)
    finally:
        _throw = True
        _exceptions.clear()


def _assertion(assertion: bool, error_msg: str):
    if not assertion:
        exception = AssertionError(error_msg)

        if _throw:
            raise exception

        _exceptions.append(exception)


def between(
    value: Any,
    left: Any,
    right: Any,
    include_left: bool = True,
    include_right: bool = True,
):
    assertion = std_between(value, left, right, include_left, include_right)
    l = 1 + include_left
    r = 1 + include_right
    error_msg = f"assert {left!r} {'<='[:l]} {value!r} {'<='[:r]} {right!r}"
    _assertion(assertion, error_msg)


def contain(container: Container, item: Any):
    _assertion(item in container, f"assert {item!r} in {container!r}")


def equal(a, b):
    _assertion(a == b, f"assert {a!r} == {b!r}")


def false(a):
    _assertion(not a, f"assert not bool({a!r})")


def greater_equal(a, b):
    _assertion(a >= b, f"assert {a!r} >= {b!r}")


def greater_than(a, b):
    _assertion(a > b, f"assert {a!r} > {b!r}")


def less_equal(a, b):
    _assertion(a <= b, f"assert {a!r} <= {b!r}")


def less_than(a, b):
    _assertion(a < b, f"assert {a!r} < {b!r}")


def same(a, b):
    _assertion(a is b, f"assert {a!r} is {b!r}")


def true(a):
    _assertion(a, f"assert bool({a!r})")
