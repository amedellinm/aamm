def qualname(obj: object) -> str:
    return type(obj).__qualname__


def attribute_error(obj: object, attribute: str) -> str:
    return f"'{qualname(obj)}' object has no attribute '{attribute}'"


def index_error(sequence: object, index: int) -> str:
    length = len(sequence)
    type_name = qualname(sequence)
    return f"index {index} out of range for {type_name!r} object of length {length}"


def key_error(key: object, mapping: object) -> str:
    return f"{key!r} not in {qualname(mapping)!r} object"


def operand_error(operator: str, *operands: tuple[object]) -> str:
    operands = ", ".join(map(repr, operands))
    return f"invalid operator '{operator}' for operand(s): {operands}"


def type_error(obtained: object, expected: type | tuple[type]) -> str:
    if isinstance(expected, type):
        expected = (expected,)
    types = " | ".join(t.__qualname__ for t in expected)
    return f"expected type(s) {types}, got {qualname(obtained)}"
