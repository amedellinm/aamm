def _qualname(obj: object) -> str:
    return type(obj).__qualname__


def attribute_error(obj: object, attribute: str) -> str:
    return f"{_qualname(obj)!r} object has no attribute {attribute!r}"


def index_error(sequence: object, index: int) -> str:
    length = len(sequence)
    type_name = _qualname(sequence)
    return f"index {index} out of range for {type_name!r} object of length {length}"


def key_error(key: object, mapping: object) -> str:
    return f"{key!r} not in {_qualname(mapping)!r} object"


def type_error(obtained: object, expected: type | tuple[type]) -> str:
    if isinstance(expected, type):
        expected = (expected,)
    types = " | ".join(repr(t.__qualname__) for t in expected)
    return f"expected {types}, got {_qualname(obtained)!r}"
