from itertools import chain

from aamm.strings import indent


def function_call(function_name: str, *args, **kwargs) -> str:
    params = ", ".join(
        chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items()))
    )
    return f"{function_name}({params})"


def tag_header_body(tag, header, body):
    return f"[{tag}] {header}\n{indent(body)}"
