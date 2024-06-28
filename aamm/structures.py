from array import array
from math import ceil
from typing import Iterable, Iterator

import numpy as np

from aamm.formats.exception import index_error
from aamm.std import cap_iter, iterbits, mod_complement


class BitArray:
    """Memory efficient array of bools"""

    def __getitem__(self, arg: int | slice) -> bool:
        if isinstance(arg, int):
            if arg >= self.length:
                raise IndexError(index_error(self, arg))
            if arg < 0:
                arg += self.length
            B = arg // 8
            b = mod_complement(arg + 1, 8)
            return bool(self.array[B] & 2**b)
        if isinstance(arg, slice):
            bools = self.as_list(arg.start, arg.stop, arg.step)
            cls = type(self)
            return cls(bools)

    def __init__(self, bools: Iterable[bool] = ()) -> None:
        self.length = len(bools)
        self.array = self.bits_to_ints(bools)

    def __iter__(self) -> Iterator:
        return cap_iter(iterbits(self.array), self.length)

    def __len__(self) -> int:
        return self.length

    def __repr__(self) -> str:
        value = f"[{', '.join('1' if bit else '0' for bit in self)}]"
        return f"{type(self).__qualname__}({value})"

    def __str__(self) -> str:
        return f"[{' '.join('1' if bit else '0' for bit in self)}]"

    def as_list(self, *slice_args) -> list[bool]:
        """Returns a slice of the array as a list."""
        bools = []
        for i in range(*slice(*slice_args).indices(self.length)):
            B = i // 8
            b = mod_complement(i + 1, 8)
            bools.append(bool(self.array[B] & 2**b))
        return bools

    @staticmethod
    def bits_to_ints(bools: Iterable[bool]) -> array:
        """Computes an `array` of bytes from an iterable of bools."""
        bools = tuple(bools)
        if not bools:
            return array("B")
        bools += mod_complement(len(bools), 8) * (False,)
        matrix = np.array(bools, dtype="bool").reshape(-1, 8)
        powers = np.array([2**p for p in range(7, -1, -1)])
        return array("B", matrix @ powers)

    def copy(self):
        """Makes a copy of the object."""
        copy = type(self)()
        copy.array = array("B", self.array)
        copy.length = self.length
        return copy

    def count(self, value: bool = True, *, percentage: bool = False) -> int | float:
        """Counts the appearances of a particular value."""
        total = sum(self) if value else self.length - sum(self)
        if percentage:
            total /= self.length
        return total

    def counts(self, *, percentage: bool = False) -> tuple[int | float]:
        """Counts the False and True values of in the array."""
        total_true = sum(self)
        total_false = self.length - total_true
        if percentage:
            total_true /= self.length
            total_false /= self.length
        return total_true, total_false

    @classmethod
    def from_ints(cls, ints: Iterable[int], length: int = None):
        """Creates a `BitArray` from an iterable of ints."""
        self = cls()

        if length is None:
            self.array = array("B", ints)
            self.length = 8 * len(self.array)
        else:
            ints = list(ints)[: ceil(length / 8)]
            self.array = array("B", ints)
            self.length = length
            if length:
                remainder = mod_complement(length, 8)
                self.array[-1] = self.array[-1] >> remainder << remainder

        return self

    @classmethod
    def ones(cls, length: int = 0):
        """Creates a `BitArray` of `length` 1s."""
        self = cls()
        self.array = array("B", ceil(length / 8) * (255,))
        self.length = length

        if length:
            remainder = mod_complement(length, 8)
            self.array[-1] = 255 >> remainder << remainder

        return self

    @classmethod
    def zeros(cls, length: int = 0):
        """Creates a `BitArray` of `length` 0s."""
        self = cls()
        self.array = array("B", ceil(length / 8) * (0,))
        self.length = length
        return self
