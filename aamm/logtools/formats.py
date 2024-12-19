from itertools import chain


def content_table_row(
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


def reprlike(obj: object, *attrs: tuple[str]) -> str:
    """Generate a repr-like string of `obj` featuring `attrs`."""
    Type = type(obj).__qualname__
    args = ", ".join(f"{attr}={getattr(obj, attr)!r}" for attr in attrs)
    return f"{Type}({args})"
