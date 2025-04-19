import importlib.util
import inspect
import io
import sys
from collections import UserDict
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import wraps
from types import GenericAlias, ModuleType
from typing import Any, Callable, Literal, TypeVar

from aamm import file_system as fs
from aamm import string

T = TypeVar("T")


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


def lazy_property(method: Callable[[Any], T]) -> T:
    """
    DESCRIPTION
    -----------
    Convert a method into a `property` whose initial value is lazyly computed upon
    accessing it for the first time.

    PARAMETERS
    ----------
    method:
        - receives `self` as a parameter.
        - runs only once.
        - its return value is used as the initial value of the property.

    """

    from aamm.logging import formats as fmts

    private_name = "_" + method.__name__
    deleted_flag = False

    def gettter(instance):

        if deleted_flag:
            raise AttributeError(fmts.attribute_error(instance, method.__name__))
        if not hasattr(instance, private_name):
            setattr(instance, private_name, method(instance))
        return getattr(instance, private_name)

    def setter(instance, value):
        setattr(instance, private_name, value)

    def deleter(instance):
        nonlocal deleted_flag
        deleted_flag = True
        delattr(instance, private_name)

    return property(gettter, setter, deleter, "hi")


def mangle(obj: Any, attr: str) -> str:
    """Return the mangled name of `attr`."""
    class_name = type(obj).__name__.removeprefix("_")
    return f"_{class_name}__{attr}"


def module_identifier(path: str) -> str:
    """Return an import-statement-valid module identifier from a path."""
    return fs.remove_extension(path).replace(fs.SEP, ".").removesuffix(".__init__")


def public_members(child_class: type) -> Iterator[tuple[str, Any, type]]:
    """
    Yield tuples of `(member_name, member, original_class)`.

    The value of `member_name` is computed as: `f"{class_name}.{attr_name}"`, where
    `class_name` is the first `class` in the MRO that defines/redefines `attr_name`.

    There are several ways in which a member can be never yielded:
        * If its name is dunder (e.g. "__attr_name__") but the member itself is not a
          callable.
        * If its name doesn't start with a letter (case-insensitive).
        * if `class_name` turns out to be `object`.

    """

    # Iterate over all members of the class, including inherited.
    for name in dir(child_class):
        # Iterate over the MRO to find the last class that defined/redefined `name`.
        for base in child_class.mro():
            # Skip `name` if it does not resemble that of a public member.
            is_dunder = string.is_dunder(name)
            if not (name[:1].isalpha() or is_dunder):
                break

            # Unlike the output of `dir`, `__dict__` contains only the symbols local to
            # the class. Which makes it ideal for telling inherited symbols apart.
            if name in base.__dict__:
                value = getattr(base, name)
                # Ignore `name` if it originated from `object`.
                if base is not object and (callable(value) or not is_dunder):
                    if inspect.ismethod(value):
                        yield f"{base.__qualname__}.{name}.__func__", value.__func__, base
                    else:
                        yield f"{base.__qualname__}.{name}", value, base
                break


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


class DictTrackUnused(UserDict):
    def __getitem__(self, key):
        """Remove `key` from unused and return its value."""
        self.__unused_keys.discard(key)
        return super().__getitem__(key)

    def __init__(self, *args, **kwargs):
        """Call the `dict` constructor."""
        self.__unused_keys = set()
        self.__all_keys = set()
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        """Add `key` to unused if it is new and set its value."""
        if key not in self.__all_keys:
            self.__all_keys.add(key)
            self.__unused_keys.add(key)
        super().__setitem__(key, value)

    def unused_keys(self) -> set:
        """Return a `set` of the unused keys at the moment of calling this method."""
        return self.__unused_keys.copy()


class Namespace(type):
    """Create not-instantiable class whose methods are static."""

    def __init__(self, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace, **kwargs)
        self.__unused_names: set[str] = {
            name for name in namespace if name[:1].isalpha()
        }

    def __call__(self):
        raise TypeError(f"namespace '{self.__qualname__}' is not instantiable")

    def __getattribute__(self, name: str):
        super().__getattribute__(mangle(self, "unused_names")).discard(name)
        return super().__getattribute__(name)

    def unused_names(self) -> Iterator[tuple[str, Any]]:
        # """Yield the name and value of all unused names in the namespace."""
        for name in dir(self):
            if not name[:1].isalpha():
                continue

            value = super().__getattribute__(name)

            if name in self.__unused_names:
                yield name, value
            if isinstance(value, type) and type(value) is Namespace:
                for sub_name, sub_value in value.unused_names():
                    yield f"{name}.{sub_name}", sub_value


class ReadOnlyProperty:
    """Allow one write operation, then become read-only."""

    def __set_name__(self, _, name):
        """Set private and display names."""
        self.display_name = name
        self.private_name = "_" + name

    def __get__(self, obj, _: type = None):
        """
        Return the value under `self.private_name` if instance, or the descriptor itself
        if class.

        """
        return self if obj is None else getattr(obj, self.private_name)

    def __set__(self, obj, value):
        """Write to the attribute. Works only once."""
        if hasattr(obj, self.private_name):
            raise AttributeError(f"property '{self.display_name}' is read-only")
        setattr(obj, self.private_name, value)
