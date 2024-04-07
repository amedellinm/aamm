import os
import sys
from contextlib import contextmanager
from functools import wraps
from time import perf_counter
from typing import Any, Callable, Literal
from weakref import finalize

import aamm.formats as fmt
from aamm.file_system import current_filename, current_folderpath


class Logger:
    END = "\n"
    FOLDER_NAME = "__logs"
    LEVEL = 0
    SEP = " "

    registry = {}

    def __call__(
        self,
        *values: tuple[str],
        end: str = None,
        sep: str = None,
        use_repr: bool = False,
    ) -> Literal[True]:
        """`print`-like interface for logging."""
        if self.enabled and self.level >= self.LEVEL:
            self.registry[self.path] = True
            self._log(*values, sep=sep, end=end, use_repr=use_repr)
        return True

    def __init__(
        self,
        file: str = None,
        root: str = None,
        *,
        clear_file: bool = False,
        enabled: bool = True,
        level: int = 0,
        separate_on_init: bool = True,
        use_stdout: bool = False,
    ) -> None:
        self.callbacks = []
        self.enabled = enabled
        self.level = level

        if use_stdout:
            self.path = None
            self.target = sys.stdout
        else:
            self.path = os.path.join(
                root or os.path.join(current_folderpath(), self.FOLDER_NAME),
                file or current_filename("log"),
            )
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.target = open(self.path, "a")

        self.registry.setdefault(self.path, True)

        if clear_file:
            self.clear_file()

        if separate_on_init:
            self.separate()

        finalize(self, self._final_dispatch)

    def __repr__(self) -> str:
        return fmt.reprlike(
            self,
            path=self.path and fmt.ellipse_path(self.path),
            enabled=self.enabled,
        )

    def _final_dispatch(self) -> None:
        try:
            for callback, args, kwargs in self.callbacks:
                callback(*args, **kwargs)
        finally:
            if self.target is not sys.stdout:
                self.target.close()

    def _log(
        self,
        *values: tuple[str],
        sep: str = None,
        end: str = None,
        use_repr: bool = False,
    ) -> None:
        end = self.END if end is None else end
        sep = self.SEP if sep is None else sep
        self.target.write(sep.join(map(repr if use_repr else str, values)) + end)

    def clear_file(self) -> Literal[True]:
        """Clears the log file the logger instance points to"""
        if self.target is not sys.stdout:
            self.target.truncate(0)
            self.target.seek(0)
        return True

    @contextmanager
    def clock(self, tag: Any = None):
        """Times code within a with block."""
        time = -perf_counter()
        try:
            yield
        finally:
            time += perf_counter()
            self(self.clock_format(tag, time))

    def clock_format(self, tag: Any, disp_decimals: int, t: float) -> str:
        return f"[CLOCK]: {tag} | {t:.{disp_decimals}f} s"

    @contextmanager
    def isolate(self, multiplier_enter: int = 1, multiplier_exit: int = 1):
        """Runs the `separate` method before and after the context."""
        self.separate(multiplier_enter)
        try:
            yield
        finally:
            self.separate(multiplier_exit)

    def profile(self, func: Callable) -> Callable:
        """Logs the call count and spend time of the decorated function."""
        call_count = 0
        total_time = 0.0

        @wraps(func)
        def decorated(*args, **kwargs):
            nonlocal call_count, total_time
            call_count += 1
            total_time -= perf_counter()
            ans = func(*args, **kwargs)
            total_time += perf_counter()
            return ans

        def callback() -> None:
            self(
                self.profile_format(
                    func.__qualname__, call_count, total_time, total_time / call_count
                )
            )

        self.callbacks.append((callback, (), {}))

        return decorated

    def profile_format(
        self, function_name: str, call_count: int, total_time: float, avg_time: float
    ) -> str:
        return fmt.logging.tag_header_body(
            "PROFILING",
            f"On function '{function_name}'",
            fmt.kwargs(call_count=call_count, total_time=total_time, avg_time=avg_time),
        )

    def separate(self, multiplier: int = 2) -> Literal[True]:
        """Logs `multiplier * self.END`. Consecutive calls do nothing."""
        if self.registry[self.path]:
            self.registry[self.path] = False
            self(multiplier * self.END, sep="", end="")
        return True

    def tracker(self, func: Callable) -> Callable:
        """Logs every time the decorated function is called with input/output info."""

        @wraps(func)
        def decorated(*args, **kwargs):
            ans = func(*args, **kwargs)
            self(self.tracker_format(func.__qualname__, args, kwargs, ans))
            return ans

        return decorated

    def tracker_format(
        self, name: str, args: tuple, kwargs: dict[str, Any], ans: Any
    ) -> str:
        return f"[TRACKER]: {fmt.call(name, *args, **kwargs)} -> {ans}"
