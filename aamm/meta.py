import inspect
import sys
from contextlib import contextmanager
from functools import wraps
from types import GenericAlias
from typing import Callable, Literal

from aamm.exceptions.formats import attribute_error
from aamm.std import qualname


@contextmanager
def capture_stdout(file_path: str, mode: str = "a"):
    """Temporarily redirect the stdout traffic to `file_path`."""
    stdout = sys.stdout
    with open(file_path, mode) as file:
        sys.stdout = file
        try:
            yield file
        finally:
            sys.stdout = stdout


def deprecation(msg: Callable | str) -> Callable:
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


def not_implemented_method(method: Callable) -> Callable:
    @wraps(method)
    def function(self, *args, **kwargs):
        raise NotImplementedError(
            f"method '{method.__name__}' not implemented in class '{qualname(self)}'"
        )

    return function


def typehint_handlers(cases: dict[type | GenericAlias, Callable]):
    def decorator(function: Callable) -> Callable:
        typehint_map = {
            arg: cases[typehint]
            for arg, typehint in function.__annotations__.items()
            if typehint in cases
        }

        signature = inspect.signature(function)

        @wraps(function)
        def decorated(*args, **kwargs):
            bound_args = signature.bind(*args, **kwargs)
            bound_args.apply_defaults()

            for arg, mapper in typehint_map.items():
                bound_args.arguments[arg] = mapper(bound_args.arguments[arg])

            return function(*bound_args.args, **bound_args.kwargs)

        return decorated

    return decorator


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


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


class ReadOnlyProperty:
    """Allow one write operation, then become read-only."""

    def __set_name__(self, _, name):
        self.display_name = name
        self.private_name = "_" + name

    def __get__(self, obj, obj_type: type = None):
        if obj is None:
            raise AttributeError(attribute_error(obj_type, self.display_name))
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if hasattr(obj, self.private_name):
            raise AttributeError(f"Property '{self.display_name}' is read-only")
        setattr(obj, self.private_name, value)
