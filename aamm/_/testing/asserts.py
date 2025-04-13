from collections.abc import Container
from contextlib import contextmanager
from operator import le, lt
from typing import Any, Callable

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


_exceptions = []
_throw = True


def _assertion(assertion: bool, error_msg: str):
    if not assertion:
        exception = AssertionError(error_msg)

        if _throw:
            raise exception

        _exceptions.append(exception)


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


@contextmanager
def assert_many(message: str = "assertion error(s)"):
    """
    Collect exceptions raised via the `asserts` module and raise them as a group at
    the end of the context.

    """
    global _exceptions, _throw
    _throw = False
    try:
        yield
        if len(_exceptions) == 1:
            raise _exceptions[0]
        if len(_exceptions) > 1:
            raise ExceptionGroup(message, _exceptions)
    finally:
        _throw = True
        _exceptions.clear()


def between(
    value: Any,
    lower: Any,
    upper: Any,
    include_lower: bool = True,
    include_upper: bool = True,
):
    """Check `value` is between `lower` and `upper`."""
    l = le if include_lower else lt
    r = le if include_upper else lt
    assertion = l(lower, value) and r(value, upper)

    l = 1 + include_lower
    r = 1 + include_upper
    error_msg = f"assert {lower!r} {'<='[:l]} {value!r} {'<='[:r]} {upper!r}"

    _assertion(assertion, error_msg)


def contain(container: Container, item: Any):
    """Assert `item in container`."""
    _assertion(item in container, f"assert {item!r} in {container!r}")


def equal(expected, obtained):
    """Assert `expected == obtained`."""
    _assertion(expected == obtained, f"assert {expected!r} == {obtained!r}")


@contextmanager
def exception_context(exception: Exception):
    """Assert `exception` is raised within the context."""
    try:
        yield
    except exception:
        return

    _assertion(False, f"assert raise '{exception.__qualname__}'")


def false(expected):
    """Assert `not expected`."""
    _assertion(not expected, f"assert not bool({expected!r})")


def greater_equal(expected, obtained):
    """Assert `expected >= obtained`."""
    _assertion(expected >= obtained, f"assert {expected!r} >= {obtained!r}")


def greater_than(expected, obtained):
    """Assert `expected > obtained`."""
    _assertion(expected > obtained, f"assert {expected!r} > {obtained!r}")


def identical(expected, obtained):
    """Assert `expected is obtained`."""
    _assertion(expected is obtained, f"assert {expected!r} is {obtained!r}")


def less_equal(expected, obtained):
    """Assert `expected <= obtained`."""
    _assertion(expected <= obtained, f"assert {expected!r} <= {obtained!r}")


def less_than(expected, obtained):
    """Assert `expected < obtained`."""
    _assertion(expected < obtained, f"assert {expected!r} < {obtained!r}")


def not_contain(container: Container, item: Any):
    """Assert `item not in container`."""
    _assertion(item not in container, f"assert {item!r} not in {container!r}")


def not_equal(expected, obtained):
    """Assert `expected != obtained`."""
    _assertion(expected != obtained, f"assert {expected!r} != {obtained!r}")


def not_identical(expected, obtained):
    """Assert `expected is not obtained`."""
    _assertion(expected is not obtained, f"assert {expected!r} is not {obtained!r}")


def raise_exception(exception: Exception, function: Callable, *args, **kwargs):
    """Assert `exception` is raised when calling `function(*args, **kwargs)`."""
    try:
        function(*args, **kwargs)
    except exception:
        return

    _assertion(False, f"assert raise '{exception.__qualname__}'")


def true(expected):
    """Assert `bool(expected)`."""
    _assertion(bool(expected), f"assert bool({expected!r})")
