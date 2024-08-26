from copy import deepcopy

import numpy as np

from aamm.meta import ReadOnlyProperty


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
        return f"{type(self).__qualname__}({self.seed})"

    def booleans(self, p: float = 0.5, size: int = None) -> bool | np.ndarray[bool]:
        """Returns the result of a Bernoulli trial as a `bool`."""
        return self.random(size) < p

    def get_state(self) -> dict:
        """Gets the rng state."""
        return deepcopy(self.bit_generator.state)

    def set_state(self, state: dict) -> None:
        """Sets the rng state."""
        self.bit_generator.state = state
