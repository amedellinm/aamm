import io
import os
import sys
from contextlib import contextmanager
from functools import wraps
from time import perf_counter
from typing import Any, Callable, Literal, Self
from weakref import finalize

import aamm.logtools.formats as fmt
from aamm.file_system import current_directory, current_file


class Logger:
    FOLDER_NAME = "__logs"

    SEP = " "
    END = "\n"

    LOG_LEVEL = 0

    separator_cache = {}

    def __init__(
        self,
        file: str = None,
        root: str = None,
        *,
        clear_file: bool = False,
        enabled: bool = True,
        log_level: int = 0,
        separate: bool = True,
        use_stdout: bool = True,
        stack_index: int = 0,
    ) -> None:
        self.buffer = io.StringIO()
        self.buffered_end = ""
        self.callbacks = []
        self.enabled = enabled
        self.log_level = log_level

        # Construct path
        stack_index += 1
        directory = current_directory(stack_index=stack_index)
        file_name = current_file("log", name_only=True, stack_index=stack_index)

        path = os.path.join(
            root or os.path.join(directory, self.FOLDER_NAME),
            file or file_name,
        )

        self.path = None if use_stdout else path
        self.separator_cache.setdefault(self.path, True)

        if use_stdout:
            self.path = None
            self.stream = sys.stdout
            self.write(f"[LOGGER] Set `use_stdout = False` to write to:\n\t{path}")
            self.separate()
        else:
            path_existed = os.path.exists(path)
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            self.stream = open(self.path, "a")

            if clear_file:
                self.clear_file()
            elif separate and path_existed:
                self.separate()

        finalize(self, self._final_dispatch)

    def __repr__(self) -> str:
        return fmt.reprlike(
            self,
            enabled=self.enabled,
            log_level=self.log_level,
            path=self.path and fmt.ellipse_path(self.path),
        )

    def _final_dispatch(self) -> None:
        """Runs when `self` is destroyed. Does callbacks/clean-up"""
        try:
            for callback, args, kwargs in self.callbacks:
                callback(*args, **kwargs)
        finally:
            if self.target is not sys.stdout:
                self.target.close()

    def _write(
        self,
        *values: tuple[str],
        sep: str = None,
        end: str = None,
        use_repr: bool = False,
    ) -> None:
        """Raw logging. Surpasses all checks and separation management"""
        end = self.END if end is None else end
        sep = self.SEP if sep is None else sep
        self.target.write(sep.join(map(repr if use_repr else str, values)) + end)

    def buffer(
        self,
        *values: tuple[Any],
        end: str = None,
        sep: str = None,
        use_repr: bool = False,
        log_level: int = None,
    ) -> Literal[True]:
        """
        DESCRIPTION
        -----------
        Runs `self.write` in a buffered manner. It has to be flushed via `self.flush`.

        PARAMETERS
        ----------
        ### end:
            - String appended at the end of the constructed message.
            - Uses `self.END` if `None`.

        ### sep:
            - String used to join `values`.
            - Uses `self.SEP` if `None`.

        ### use_repr:
            - Decides how to convert `values` to strings.
            - If `True` uses `repr`.
            - If `False` uses `str`.

        ### log_level:
            - Level of the log operation.
            - If `None` uses `self.log_level`.
            - A log_level lower than `self.LOG_LEVEL` wont log.

        RETURNS
        -------
        ### bool:
            - A literal `True`.

        """
        self.target, target = self._buffer, self.target
        self.write(*values, end, sep, use_repr, log_level)
        self.target = target
        return True

    @contextmanager
    def capture_stderr(self):
        with self.capture_stream(sys.stderr):
            yield

    @contextmanager
    def capture_stdout(self):
        with self.capture_stream(sys.stdout):
            yield

    @contextmanager
    def capture_stream(self, stream: io.TextIOBase):
        write, stream.write = stream.write, self.target.write
        try:
            yield
        finally:
            stream.write = write

    def clear_file(self) -> Literal[True]:
        """Clears the file the logger instance points to"""
        if self.stream is not sys.stdout:
            self.stream.seek(0)
            self.stream.truncate(0)
        return True

    def flush(self) -> Literal[True]:
        self.stream.write(self.buffer.getvalue())
        self.buffer.seek(0)
        self.buffer.truncate(0)
        return True

    @contextmanager
    def isolate(self, multiplier_enter: int = 1, multiplier_exit: int = 1):
        """Runs the `separate` method before and after the context."""
        self.separate(multiplier_enter)
        yield
        self.separate(multiplier_exit)

    def separate(self, multiplier: int = 2) -> Literal[True]:
        """Logs `multiplier * self.END`. Consecutive calls do nothing."""
        if self.separator_cache[self.path]:
            self.separator_cache[self.path] = False
            self.buffered_end = ""
            self.write("", sep="", end=(multiplier + 1) * self.END)

        return True

    @classmethod
    def set_global_log_level(cls, log_level: int) -> Literal[True]:
        """For all instances, sets the minimum log_level required to log"""
        cls.LOG_LEVEL = log_level
        return True

    @contextmanager
    def using(self, **temporal_values):
        """Runs the `separate` method before and after the context."""
        original_values = {attr: getattr(self, attr) for attr in temporal_values}
        for attr, value in temporal_values.items():
            setattr(self, attr, value)
        try:
            yield
        finally:
            for attr, value in original_values.items():
                setattr(self, attr, value)

    def write(
        self,
        *values: tuple[Any],
        end: str = None,
        sep: str = None,
        use_repr: bool = False,
        log_level: int = None,
        flush: int = True,
    ) -> Literal[True]:
        """
        DESCRIPTION
        -----------
        This is the Main method of the class. It provides a `print`-like interface for
        logging.

        PARAMETERS
        ----------
        ### end:
            - String appended at the end of the constructed message.
            - Uses `self.END` if `None`.

        ### sep:
            - String used to join `values`.
            - Uses `self.SEP` if `None`.

        ### use_repr:
            - Decides how to convert `values` to strings.
            - If `True` uses `repr`.
            - If `False` uses `str`.

        ### log_level:
            - Level of the log operation.
            - If `None` uses `self.log_level`.
            - A log_level lower than `self.LOG_LEVEL` wont log.

        RETURNS
        -------
        ### bool:
            - A literal `True`.

        """
        log_level = self.log_level if log_level is None else log_level

        if self.enabled and log_level >= self.LOG_LEVEL:
            self.separator_cache[self.path] = True
            end = self.END if end is None else end
            sep = self.SEP if sep is None else sep
            msg = self.buffered_end + sep.join(map(repr if use_repr else str, values))
            self.buffered_end = end

            self.buffer.write(msg)

            if flush:
                self.flush()

        return True


class Timer(Logger):
    @contextmanager
    def clock(self, tag: Any = None):
        """Times code within a `with` block."""
        time = -perf_counter()
        yield
        self.write(self.clock_format(tag, time + perf_counter()))

    def clock_format(self, tag: Any, time: float) -> str:
        return f"{tag} | {time:.6f} s"

    def profile(self, function: Callable) -> Callable:
        """Logs the call count and spend time of the decorated function."""
        call_count = 0
        total_time = 0.0

        @wraps(function)
        def decorated(*args, **kwargs):
            nonlocal call_count, total_time
            call_count += 1
            total_time -= perf_counter()
            ans = function(*args, **kwargs)
            total_time += perf_counter()
            return ans

        def callback() -> None:
            self.write(
                self.profile_format(
                    function.__qualname__,
                    call_count,
                    total_time,
                    total_time / call_count,
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
            fmt.kwargs(
                call_count=call_count, total_time=total_time, avg_time=avg_time
            ),
        )

    def tracker(self, func: Callable) -> Callable:
        """Logs every time the decorated function is called with input/output info."""

        @wraps(func)
        def decorated(*args, **kwargs):
            ans = func(*args, **kwargs)
            self.write(self.tracker_format(func.__qualname__, args, kwargs, ans))
            return ans

        return decorated

    def tracker_format(
        self, name: str, args: tuple, kwargs: dict[str, Any], ans: Any
    ) -> str:
        return f"[TRACKER]: {fmt.call(name, *args, **kwargs)} -> {ans!r}"
