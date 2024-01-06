from typing import Any, Sequence

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def qualname(obj: Any) -> str:
    return type(obj).__qualname__


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def attribute_error(obj: Any, attribute: str) -> str:
    return f"'{qualname(obj)}' object has no attribute '{attribute}'"


def index_error(sequence: Sequence, index: int) -> str:
    length = len(sequence)
    type_name = qualname(sequence)
    return f"Index {index} out of range for {type_name} of length {length}"


def key_error(key: Any) -> str:
    return f"key error: {key!r}"


def operand_error(operand: str, a: type, b: type) -> str:
    type_1 = qualname(a)
    type_2 = qualname(b)
    return f"unsupported operand type(s) for {operand!r}: {type_1!r} and {type_2!r}"


def type_error(expected: Any, obtained: Any) -> str:
    return f"expected {qualname(expected)}, but got {qualname(obtained)}"
