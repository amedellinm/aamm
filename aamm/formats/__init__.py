import os
from itertools import chain
from typing import Any, Iterable

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


def call(name: str, *args, **kwargs) -> str:
    params = ", ".join(
        chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items()))
    )
    return f"{name}({params})"


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
    args_format = [repr(a) for a in args]
    kwargs_format = [f"{k}={v!r}" for k, v in kwargs.items()]
    parameters = ", ".join(args_format + kwargs_format)
    return f"{function_name}({parameters})"


def indent(string: str, level: int = 1) -> str:
    return (level * "\t" + string.strip()).replace("\n", "\n" + level * "\t")


def kwargs(
    indent_level: int = 0,
    line_start: str = "",
    connector: str = " = ",
    line_end: str = "\n",
    end: str = "",
    **kwargs,
) -> str:
    return vectors(kwargs.items(), indent_level, line_start, connector, line_end, end)


def qualname(obj: Any) -> str:
    """Returns the qualname of an object's type"""
    return type(obj).__qualname__


def reprlike(obj: object, **kwargs) -> str:
    body = indent("\n".join(f"{k}={v!r}," for k, v in kwargs.items()))
    return f"{obj.__class__.__qualname__}(\n" + body + "\n)"


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


def wrap(text: str, row_length: int = 88, sep=" ", new_line="\n") -> str:
    text = text.strip() + sep
    indices = {0}
    last = old = 0

    for new, char in enumerate(text):
        if char == sep:
            if new - last > row_length:
                indices.add(old)
                last = old
            old = new

    indices.remove(0)

    return "".join(
        new_line if i in indices else char for i, char in enumerate(text[:-1])
    )
