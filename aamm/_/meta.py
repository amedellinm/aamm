import importlib.util
import inspect
import io
import sys
from collections import Counter
from contextlib import contextmanager
from functools import wraps
from types import GenericAlias, ModuleType
from typing import Any, Callable, Literal

from aamm import file_system as fs


@contextmanager
def capture_stdout(stream: io.TextIOBase):
    """Temporarily redirect the stdout traffic to `stream`."""
    stdout, sys.stdout = sys.stdout, stream
    try:
        yield stream
    finally:
        sys.stdout = stdout


def import_path(path: str) -> ModuleType:
    """Import a Python module (.py) from a path using its absolute version as name."""
    name = module_identifier(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def module_identifier(path: str) -> str:
    return fs.remove_extension(path).replace(fs.SEP, ".").removesuffix(".__init__")


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


class Namespace(type):
    """Create not-instantiable class whose methods are static."""

    def __new__(cls, name: str, bases: tuple[type, ...], dctn: dict[str, Any]):
        if bases:
            raise ValueError("`Namespace` does not support inheritance")

        namespace = super().__new__(cls, name, (), dctn)
        members = {k: v for k, v in vars(namespace).items() if k.isalpha()}

        class Instance:
            __slots__ = tuple(members)

        instance = Instance()

        for item in members.items():
            setattr(instance, *item)

        return instance


class NamespaceTrackUnused(type):
    """Create a `Namespace` with a special `_unused_names` method."""

    def __new__(cls, name: str, bases: tuple[type, ...], dctn: dict[str, Any]):
        if bases:
            raise ValueError("`Namespace` does not support inheritance")

        namespace = super().__new__(cls, name, (), dctn)
        members = {k: v for k, v in vars(namespace).items() if k.isalpha()}

        unused_names = set(members)

        class Instance:
            __slots__ = tuple(members)

            def __getattribute__(self, name: str):
                unused_names.discard(name)
                return super().__getattribute__(name)

            @staticmethod
            def _unused_names() -> list[str]:
                return sorted(unused_names)

        instance = Instance()

        for item in members.items():
            setattr(instance, *item)

        return instance


class ReadOnlyProperty:
    """Allow one write operation, then become read-only."""

    def __set_name__(self, _, name):
        self.display_name = name
        self.private_name = "_" + name

    def __get__(self, obj, _: type = None):
        return self if obj is None else getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if hasattr(obj, self.private_name):
            raise AttributeError(f"property '{self.display_name}' is read-only")
        setattr(obj, self.private_name, value)
