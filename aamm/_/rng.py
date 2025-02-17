from copy import deepcopy
from typing import Any

import numpy as np

from aamm import meta


class RNG(np.random.Generator):
    """`RNG` is an extension of `numpy.random.Generator`"""

    seed = meta.ReadOnlyProperty()

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
        """Return the result of Bernoulli trials as `bool`s."""
        return self.random(size) < p

    def get_state(self) -> dict[str, Any]:
        """Get the rng state."""
        return deepcopy(self.bit_generator.state)

    def set_state(self, state: dict[str, Any]) -> None:
        """Set the rng state."""
        self.bit_generator.state = state


def create_state(seed: int | None) -> dict[str, Any]:
    """Create a state suitable for `RNG.set_state`."""
    return RNG(seed).get_state()
