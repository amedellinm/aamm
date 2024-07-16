from numbers import Number


def qualname(obj: object) -> str:
    return type(obj).__qualname__


class DomainError(ValueError):
    _ends = "([)]"

    def __init__(
        self,
        value: Number,
        left: Number,
        right: Number,
        closed_left: bool = True,
        closed_right: bool = True,
    ) -> None:
        l = self._ends[closed_left]
        r = self._ends[closed_right + 2]
        super().__init__(f"{value} outside of {l}{left}, {right}{r}")


class OperandError(TypeError):
    def __init__(self, a: object, b: object, operator: str) -> None:
        A = qualname(a)
        B = qualname(b)
        super().__init__(
            f"unsupported types '{A}' and '{B}' for operator '{operator}'"
        )