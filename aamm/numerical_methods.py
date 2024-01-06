from abc import ABCMeta, abstractmethod
from typing import Iterable

import numpy as np


class LinearRegression(metaclass=ABCMeta):
    def __call__(self, input: np.ndarray) -> np.ndarray:
        """Predicts an output for the given input."""
        return self.extend_x(input) @ self.w

    def __init__(self, x: np.ndarray, y: np.ndarray) -> None:
        x = self.extend_x(x)
        self.w = np.linalg.inv(x.T @ x) @ x.T @ y

    @abstractmethod
    def extend_x(self, x: np.ndarray) -> np.ndarray:
        """Computes the matrix that left-multiplies W in the prediction operation"""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}(W = {self.w})"


class PolynomialLinearRegression(LinearRegression):
    def __init__(self, x: np.ndarray, y: np.ndarray, powers: Iterable[float]) -> None:
        self.powers = powers
        super().__init__(x, y)
        self.weights = dict(zip(self.powers, self.w))

    def extend_x(self, X: np.ndarray) -> np.ndarray:
        return np.array([X**p for p in self.powers]).T
