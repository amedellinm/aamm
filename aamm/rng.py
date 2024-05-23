from copy import deepcopy

import numpy as np

from aamm.std import ReadOnlyProperty


class RNG(np.random.Generator):
    """`RNG` is an extension of `numpy.random.Generator`"""

    seed = ReadOnlyProperty()

    def __init__(
        self,
        seed: int = None,
        bit_generator: np.random.BitGenerator = np.random.PCG64,
    ):
        self.seed = int(np.random.random() * 10**15) if seed is None else seed
        super().__init__(bit_generator(self._seed))

    def __repr__(self) -> str:
        return f"RNG({self.seed})"

    def __str__(self) -> str:
        return f"RNG({self.seed})"

    def booleans(self, p: float = 0.5, size: int = None) -> bool | np.ndarray[bool]:
        """Returns the result of a Bernoulli trial as a `bool`."""
        return self.random(size) < p

    def get_state(self) -> dict:
        """Gets the rng state."""
        return deepcopy(self.bit_generator.state)

    def set_state(self, state: dict) -> None:
        """Sets the rng state."""
        self.bit_generator.state = state

    def indices(self, n: int, *range_args) -> np.ndarray[int]:
        """Returns n `random elements from `range(*range_args)`."""
        return self.choice(range(*range_args), n, False)

    def interval(
        self,
        lo: int,
        max_hi: int = None,
        step: int = 1,
        *,
        allow_empty: bool = False,
    ) -> range:
        """Returns a random upper bounded range from `lo` to at most `max_hi`."""

        if max_hi is None:
            max_hi, lo = lo, 0
        return range(lo, self.integers(lo + (not allow_empty), max_hi + 1), step)

    def stair(self, steps: int, length: int) -> np.ndarray[int]:
        """Return a 1D stair array of ints. `steps` is an upper limit"""
        return np.sort(self.integers(0, steps, length))
