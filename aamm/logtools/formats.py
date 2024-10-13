from itertools import chain


def _qualname(obj: object) -> str:
    return type(obj).__qualname__


def attribute_error(obj: object, attribute: str) -> str:
    return f"{_qualname(obj)!r} object has no attribute {attribute!r}"


def function_call(function_name: str, *args, **kwargs) -> str:
    params = ", ".join(
        chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items()))
    )
    return f"{function_name}({params})"


def index_error(sequence: object, index: int) -> str:
    length = len(sequence)
    type_name = _qualname(sequence)
    return f"index {index} out of range for {type_name!r} object of length {length}"


def key_error(key: object, mapping: object) -> str:
    return f"{key!r} not in {_qualname(mapping)!r} object"


def reprlike(obj: object, **kwargs) -> str:
    obj_class = type(obj).__qualname__
    repr_body = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    return f"{obj_class}({repr_body})"


def type_error(obtained: object, expected: type | tuple[type]) -> str:
    if isinstance(expected, type):
        expected = (expected,)
    types = " | ".join(t.__qualname__ for t in expected)
    return f"expected type(s) {types}, got {_qualname(obtained)}"
