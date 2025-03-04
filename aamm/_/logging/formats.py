from itertools import chain
from typing import Any


def function_call(function_name: str, *args, **kwargs) -> str:
    """Generate a string resembling a function call."""
    params = ", ".join(
        chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items()))
    )
    return f"{function_name}({params})"


def reprlike(obj: object, *attrs: tuple[str]) -> str:
    """Generate a repr-like string of `obj` featuring `attrs`."""
    Type = type(obj).__qualname__
    args = ", ".join(f"{attr}={getattr(obj, attr)!r}" for attr in attrs)
    return f"{Type}({args})"


def contents_table_row(left: Any, right: Any, width: int = 88) -> str:
    l = str(left)
    r = str(right)
    width -= len(l) + len(r) + 2
    return f"{l} {'.' * width} {r}"
