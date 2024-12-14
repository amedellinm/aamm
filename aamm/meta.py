import importlib.util
import inspect
import io
import os
import sys
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from types import GenericAlias, ModuleType
from typing import Callable, Literal

from aamm.exception_message import attribute_error


@contextmanager
def capture_stdout(stream: io.TextIOBase):
    """Temporarily redirect the stdout traffic to `stream`."""
    stdout, sys.stdout = sys.stdout, stream
    try:
        yield stream
    finally:
        sys.stdout = stdout


def import_path(path: str | Path) -> ModuleType:
    """Imports a Python module (.py) from a path"""
    module_name, _ = os.path.splitext(os.path.basename(path))
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def typehint_handlers(cases: dict[type | GenericAlias, Callable]) -> Callable:
    """
    DESCRIPTION
    -----------
    Generate a decorator that transforms the arguments passed to the decorated function
    base on their typehints.

    PARAMETERS
    ----------
    cases:
        * The mapping indicates how to transform each argument.
        * Keys are valid typehints.
        * Values are callables that receive, transform, and return a single
          argument.
        * Typehints not present in the mapping are left unchanged.

    """

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

    PARAMETERS
    ----------
    boolean_methods:
        * The mapping indicates the boolean operations to fix and their value.
        * Keys are valid boolean dunder methods.
        * Values are the booleans always returned by the methods.
        * Dunder method names are not validated.

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


class NameSpace(type):
    """Empty, non-instantiable metaclass"""

    def __new__(cls, name, bases, dctn):
        def init(self, *args, **kwargs):
            raise RuntimeError(
                f"namespace '{type(self).__qualname__}' is not instantiable"
            )

        dctn["__slots__"] = ()
        dctn["__init__"] = init

        return super().__new__(cls, name, bases, dctn)


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
            raise AttributeError(f"property '{self.display_name}' is read-only")
        setattr(obj, self.private_name, value)
