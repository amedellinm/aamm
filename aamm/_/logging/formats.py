import traceback as tb
from collections.abc import Container, Sequence
from itertools import chain
from traceback import extract_tb
from types import TracebackType
from typing import Any, Literal

from aamm import file_system as fs
from aamm.logging import Logger


def qualname(obj: Any) -> str:
    """The fully qualified name of the type of `obj`."""
    return type(obj).__qualname__


def attribute_error(obj: Any, attribute: str) -> str:
    """Return a message sutable for an attribute error exception."""
    return f"'{qualname(obj)}' object has no attribute '{attribute}'"


def contents_table_row(left: Any, right: Any, width: int = 88) -> str:
    """
    Return a contents-table-like row. `left` and `right` are aligned and connected by a
    series of dots.

    """
    l = str(left)
    r = str(right)
    width -= len(l) + len(r) + 2
    return f"{l} {'.' * width} {r}"


def exception_message(exception: Exception) -> str:
    """Return the exception message with Exception Name: message as in usual Python."""
    msg = str(exception).strip() or "`no error message`"
    return f"{type(exception).__qualname__}: {msg}"


def function_call(function_name: str, *args, **kwargs) -> str:
    """Generate a string resembling a function call."""
    params = ", ".join(
        chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items()))
    )
    return f"{function_name}({params})"


def index_error(sequence: Any, index: int) -> str:
    """Return a message sutable for an index error exception."""
    length = len(sequence)
    type_name = qualname(sequence)
    return f"index {index} out of range for {type_name!r} object of length {length}"


def key_error(mapping: Any, key: Any) -> str:
    """Return a message sutable for a key error exception."""
    return f"{key!r} not in {qualname(mapping)!r} object"


def operand_error(operator: str, *operands: tuple[object]) -> str:
    """Return a message sutable for an operand error exception."""
    operands = ", ".join(map(repr, operands))
    return f"invalid operator '{operator}' for operand(s): {operands}"


def table(
    *columns: tuple[Sequence[str]],
    alignment: Literal["left", "right"] = "left",
    spacing: str = "  ",
    newline: str = "\n",
):
    """
    Return a properly aligned table given a sequence of columns.
    `spacing` is used between columns.
    `newline` is used between rows.

    """
    if alignment == "left":
        just = str.ljust
    elif alignment == "right":
        just = str.rjust
    else:
        raise ValueError(f"expected 'left' or 'right' for `alignment`, got {alignment}")

    alignments = tuple(map(max, map(lambda column: map(len, column), columns)))

    return newline.join(
        spacing.join(just(item, alignment) for item, alignment in zip(row, alignments))
        for row in zip(*columns)
    )


def traceback(
    arg: Exception | TracebackType | tb.StackSummary,
    ignore_paths: Container[str],
    lines_around: int = 6,
) -> str:
    """Write the traceback of an exception in a more human-friendly way."""
    if isinstance(arg, Exception):
        stack = extract_tb(arg.__traceback__)
    elif isinstance(arg, TracebackType):
        stack = extract_tb(arg)
    else:
        stack = arg

    padding = len(str(max(f.lineno for f in stack) + lines_around))
    logger = Logger.from_string_io()

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
                    f"{marker} {str(line_number).rjust(padding)}: {line}", end=""
                )

        logger.separate(1)

    return logger.stream.getvalue().rstrip()


def type_error(obtained: Any, expected: type | tuple[type]) -> str:
    """Return a message sutable for a type error exception."""
    if isinstance(expected, type):
        expected = (expected,)
    types = " | ".join(t.__qualname__ for t in expected)
    return f"expected type(s) {types}, got {qualname(obtained)}"


def underlined_title(title: Any, underline: str = "-") -> str:
    """Return `str(title)` underlined by the char in `underline` (in a new line)."""
    return f"{title}\n{len(title) * underline}"
