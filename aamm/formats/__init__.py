import os
from itertools import chain
from typing import Iterable

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def abbreviate_path(path: str) -> str:
    path = os.path.relpath(path)
    parts = path.split(os.path.sep)
    if len(parts) < 3:
        return path
    head, *_, tail = parts
    return os.path.sep.join((head, "...", tail))


def bullets(iterable: Iterable, prefix: str = " - ", use_repr: bool = False) -> str:
    return prefix + ("\n" + prefix).join(map(repr if use_repr else str, iterable))


def function_call(function_name: str, *args, **kwargs) -> str:
    params = ", ".join(
        chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items()))
    )
    return f"{function_name}({params})"


def reprlike(obj: object, **kwargs) -> str:
    obj_class = type(obj).__qualname__
    repr_body = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"{obj_class}({repr_body})"
