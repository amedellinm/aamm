import io
import traceback as tb
from collections.abc import Container
from itertools import chain
from traceback import extract_tb
from types import TracebackType
from typing import Any

from aamm import file_system as fs
from aamm.logging import Logger


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


def exception_message(exception: Exception) -> str:
    return f"{type(exception).__qualname__}: {exception}"


def traceback(
    arg: Exception | TracebackType | tb.StackSummary,
    ignore_paths=Container[str],
    lines_around: int = 6,
) -> str:
    if isinstance(arg, Exception):
        stack = extract_tb(arg.__traceback__)
    elif isinstance(arg, TracebackType):
        stack = extract_tb(arg)
    else:
        stack = arg

    padding = len(str(max(f.lineno for f in stack) + lines_around))
    logger = Logger(io.StringIO())

    for frame in stack:
        if frame.filename in ignore_paths:
            continue

        # Make path relative to `root` for brevity.
        filename = fs.relative(frame.filename)

        logger.write(f"{filename}  ({frame.name})")

        try:
            with open(frame.filename, "r") as file:
                i = max(0, frame.lineno - lines_around - 1)
                j = frame.lineno + lines_around
                lines = file.readlines()[i:j]

        except:
            logger.write(f"~~~ unabled to output traceback")

        else:
            # Log the traceback if it was possible to read the file.
            for line_number, line in enumerate(lines, i + 1):
                marker = "-->" if line_number == frame.lineno else "   "

                logger.write(
                    f"{marker} {str(line_number).rjust(padding)}: {line.rstrip()}"
                )

        logger.separate(1)

    return logger.stream.getvalue()
