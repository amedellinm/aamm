from itertools import chain


def function_call(function_name: str, *args, **kwargs) -> str:
    params = ", ".join(
        chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items()))
    )
    return f"{function_name}({params})"


def reprlike(obj: object, **kwargs) -> str:
    obj_class = type(obj).__qualname__
    repr_body = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"{obj_class}({repr_body})"
