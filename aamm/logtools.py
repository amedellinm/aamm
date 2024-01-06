import os
import sys
from contextlib import contextmanager
from functools import wraps
from time import perf_counter
from typing import Any, Callable, ContextManager
from weakref import finalize

import aamm.formats as fmt
from aamm.file_system import current_filename, current_folderpath


class Logger:
    END = "\n"
    SEP = " "
    FOLDER_NAME = "__logs"

    registry = {}

    def __call__(self, *messages: tuple[str], end: str = None, sep: str = None) -> None:
        Logger.registry[self.path] = True
        self._log(*messages, sep=sep, end=end)

    def __init__(
        self,
        file: str = None,
        root: str = None,
        *,
        clear_file: bool = True,
        do_logging: bool = True,
        use_stdout: bool = False,
    ) -> None:
        self.callbacks = []
        self.do_logging = do_logging

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
            if clear_file:
                self.clear_file()

        Logger.registry.setdefault(self.path, True)
        self.split()

        finalize(self, self._final_dispatch)

    def __repr__(self) -> str:
        return fmt.reprlike(
            self,
            path=self.path and fmt.ellipse_path(self.path),
            do_logging=self.do_logging,
        )

    def _final_dispatch(self) -> None:
        for callback, args, kwargs in self.callbacks:
            callback(*args, **kwargs)
        if self.target is not sys.stdout:
            self.target.close()

    def _log(self, *messages: tuple[str], sep: str = None, end: str = None) -> None:
        if self.do_logging:
            end = self.END if end is None else end
            sep = self.SEP if sep is None else sep
            self.target.write(sep.join(map(str, messages)) + end)

    def clear_file(self) -> None:
        """Clears the log file the logger instance points to"""
        if self.target is not sys.stdout:
            self.target.truncate(0)
            self.target.seek(0)

    @contextmanager
    def clock(self, tag: Any = None, disp_decimals: int = None) -> ContextManager:
        """Times code within a with context."""
        t = -perf_counter()
        try:
            yield
        finally:
            t += perf_counter()
            self(self.clock_format(tag, disp_decimals, t))

    def clock_format(self, tag: Any, disp_decimals: int, t: float) -> str:
        return f"[CLOCK]: {tag} | {t:.{disp_decimals}f} s"

    @contextmanager
    def isolate(self) -> ContextManager:
        """Runs the split method before and after the context."""
        self.split()
        try:
            yield
        finally:
            self.split()

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

        def show_results() -> None:
            avg_time = total_time / call_count
            self(self.profile_format(func.__name__, call_count, total_time, avg_time))

        self.callbacks.append((show_results, (), {}))

        return decorated

    def profile_format(
        self, function_name: str, call_count: int, total_time: float, avg_time: float
    ) -> str:
        return fmt.logging.tag_header_body(
            "PROFILING",
            f"On function '{function_name}'",
            fmt.kwargs(call_count=call_count, total_time=total_time, avg_time=avg_time),
        )

    def split(self, gap: int = 1) -> None:
        """Logs a new line only if the last log wasn't a `self.split()` log."""
        if Logger.registry[self.path]:
            Logger.registry[self.path] = False
            self._log(gap * self.END, sep="", end="")

    def tracker(self, func: Callable) -> Callable:
        """Logs every time the decorated function is called with input/output info."""

        @wraps(func)
        def decorated(*args, **kwargs):
            ans = func(*args, **kwargs)
            call = fmt.call(func.__qualname__, *args, **kwargs)
            self(self.tracker_format(f"{call} -> {ans!r}"))
            return ans

        return decorated

    def tracker_format(self, call_signature: str) -> str:
        return f"[TRACKER]: {call_signature}"
