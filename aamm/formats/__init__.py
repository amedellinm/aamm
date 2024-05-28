import os
from itertools import chain
from typing import Iterable

from aamm.strings import indent

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def abbreviate_path(path: str) -> str:
    path = os.path.relpath(path)
    parts = path.split(os.path.sep)
    if len(parts) < 3:
        return path
    head, *_, tail = path.split(os.path.sep)
    return head + os.path.sep + "..." + os.path.sep + tail


def bullets(elements: Iterable, indent_level: int = 0, bullets: str = " - ") -> str:
    indentation = indent_level * "\t"
    return indentation + ("\n" + indentation).join(bullets + str(e) for e in elements)


def dictionary(
    dictionary: dict,
    indent_level: int = 0,
    line_start: str = "",
    connector: str = ": ",
    line_end: str = "\n",
    end: str = "",
) -> str:
    return vectors(
        dictionary.items(), indent_level, line_start, connector, line_end, end
    )


def function_call(function_name: str, *args, **kwargs) -> str:
    params = ", ".join(
        chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items()))
    )
    return f"{function_name}({params})"


def kwargs(
    indent_level: int = 0,
    line_start: str = "",
    connector: str = " = ",
    line_end: str = "\n",
    end: str = "",
    **kwargs,
) -> str:
    return vectors(kwargs.items(), indent_level, line_start, connector, line_end, end)


def reprlike(obj: object, **kwargs) -> str:
    body = indent("\n".join(f"{k}={v!r}," for k, v in kwargs.items()))
    return f"{type(obj).__qualname__}(\n{body}\n)"


def vectors(
    data: Iterable[Iterable],
    indent_level: int,
    line_start: str,
    connector: str,
    line_end: str,
    end: str,
):
    line_start = indent_level * "\t" + line_start
    return (
        line_end.join(f"{line_start}{connector.join(map(str, vec))}" for vec in data)
        + end
    )
