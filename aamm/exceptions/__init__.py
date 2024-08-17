from aamm.std import between

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def qualname(obj: object) -> str:
    return type(obj).__qualname__


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def assert_domain(
    label: str,
    value,
    left,
    right,
    include_left: bool = True,
    include_right: bool = True,
    *,
    throw: bool = False,
):
    if not between(value, left, right, include_left, include_right):
        e = DomainError(label, value, left, right, include_left, include_right)
        if throw:
            raise e
        return e


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


class DomainError(ValueError):
    def __init__(
        self,
        label,
        value,
        left,
        right,
        include_left: bool = True,
        include_right: bool = True,
    ) -> None:
        l = "<="[: 1 + include_left]
        r = "<="[: 1 + include_right]
        super().__init__(f"expected {left} {l} {label} {r} {right}, got {value}")


class OperandError(TypeError):
    def __init__(self, a: object, b: object, operator: str) -> None:
        A = qualname(a)
        B = qualname(b)
        super().__init__(
            f"unsupported types '{A}' and '{B}' for operator '{operator}'"
        )
