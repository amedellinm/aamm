from itertools import chain

from aamm.strings import indent


def content_table(
    left: str, right: str, filler: str = ".", line_length: int = 88
) -> str:
    middle = " " + (line_length - 2 - len(left) - len(right)) * filler + " "
    return left + middle + right


def function_call(function_name: str, *args, **kwargs) -> str:
    """Generate a string resembling a function call."""
    params = ", ".join(
        chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items()))
    )
    return f"{function_name}({params})"


def reprlike(obj: object, *attrs: tuple[str], line_length=88) -> str:
    """Generate a repr-like string of `obj` featuring `attrs`."""
    args = tuple(f"{attr}={getattr(obj, attr)!r}" for attr in attrs)
    name = type(obj).__qualname__
    body = (
        "\n    " + ",\n    ".join(args) + ",\n"
        if len(name) + 2 * len(args) + sum(map(len, args)) > line_length
        else ", ".join(args)
    )

    return f"{name}({body})"


def tag_header_body(tag, header, body) -> str:
    return f"[{tag}]: {header}\n{indent(body)}"
