# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def qualname(obj: object) -> str:
    return type(obj).__qualname__


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def attribute_error(obj: object, attribute: str) -> str:
    return f"{qualname(obj)!r} object has no attribute {attribute!r}"


def index_error(sequence: object, index: int) -> str:
    length = len(sequence)
    type_name = qualname(sequence)
    return f"index {index} out of range for {type_name!r} object of length {length}"


def key_error(key: object, mapping: object) -> str:
    return f"{key!r} not in {qualname(mapping)!r} object"


def type_error(obtained: object, expected: type | tuple[type]) -> str:
    if isinstance(expected, type):
        expected = (expected,)
    types = " | ".join(repr(t.__qualname__) for t in expected)
    return f"expected {types}, got {qualname(obtained)!r}"


class OperandError(TypeError):
    message_format = "unsupported type(s) {!r} and {!r} for operator {!r}".format

    def __init__(self, operator: str, a: object, b: object):
        super().__init__(self.message_format(qualname(a), qualname(b), operator))
