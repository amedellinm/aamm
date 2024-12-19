import io
import os
import sys
from contextlib import contextmanager
from typing import Any, Literal, Self, TextIO
from weakref import finalize

import aamm.file_system as fs
import aamm.logtools.formats as fmts
from aamm.meta import ReadOnlyProperty


class Logger:
    """
    DESCRIPTION
    -----------
    This is the Main method of the class. It provides a `print`-like interface for
    logging.

    PARAMETERS
    ----------
    stream:
        * Stream to write to.

    enabled:
        * If `False`, logging is suppressed.

    unmanaged:
        * If `True`, the caller manages `stream`.
        * Read only.

    """

    DIR_NAME = "__logs"

    sep = " "
    end = "\n"
    sep_registry = {}

    unmanaged = ReadOnlyProperty()

    def __init__(
        self, stream: TextIO, enabled: bool = True, unmanaged: bool = False
    ) -> None:
        self.stream = stream
        self.enabled = enabled
        self.unmanaged = unmanaged

        self.buffer = io.StringIO()
        self.sep_registry.setdefault(stream, True)

        if not unmanaged:
            finalize(self, self.stream.close)

    def __repr__(self) -> str:
        return fmts.reprlike(self, "stream", "enabled", "unmanaged")

    def clear_buffer(self) -> Self:
        """Clear buffer."""
        self.buffer.seek(0)
        self.buffer.truncate(0)
        return self

    def clear_stream(self) -> Self:
        """Clear stream."""
        self.stream.seek(0)
        self.stream.truncate(0)
        return self

    def flush(self) -> Self:
        """Dump `self.buffer` to `self.stream` though `self.write`."""
        return self.write(end="", flush=True)

    @classmethod
    def from_current_file(cls, stack_index=0) -> Self:
        """
        Construct a `Logger` instance using a stream that points to the file defined
        by joining the path segments:
            * The directory where the caller's source file lives
            * A folder named `cls.DIR_NAME`
            * A .log file of the same name as the caller's source file

        """
        stack_index += 1
        path = fs.here(
            cls.DIR_NAME,
            fs.current_file("log", True, stack_index=stack_index),
            stack_index=stack_index,
        )

        os.makedirs(fs.up(path), exist_ok=True)
        return cls(open(path, "a"))

    @classmethod
    def from_sys_stream(
        cls, stream_name: Literal["stdout", "stderr"] = "stdout"
    ) -> Self:
        """Construct a `Logger` instance using a stream from the `sys` module."""
        if stream_name in ("stdout", "stderr"):
            return cls(getattr(sys, stream_name), unmanaged=True)
        raise ValueError(f"expected 'stdout' or 'stderr', got {stream_name!r}")

    @contextmanager
    def isolate(self, multiplier_enter: int = 2, multiplier_exit: int = 2):
        """Run the `separate` method before and after the context."""
        self.separate(multiplier_enter)
        yield
        self.separate(multiplier_exit)

    def separate(self, multiplier: int = 2) -> Self:
        """Log `multiplier * self.end` idempotently."""
        if self.sep_registry[self.stream]:
            self.write(end=multiplier * self.end, flush=False)
            self.sep_registry[self.stream] = False

        return self

    @contextmanager
    def using_stream(self, stream: io.TextIOBase):
        """Temporarily replace `self.stream`."""
        self.stream, tmp = stream, self.stream
        try:
            yield
        finally:
            self.stream = tmp

    def write(
        self,
        *values: tuple[Any],
        end: str = None,
        sep: str = None,
        use_repr: bool = False,
        flush: int = True,
    ) -> Self:
        """
        DESCRIPTION
        -----------
        This is the Main method of the class. It provides a `print`-like interface for
        logging.

        PARAMETERS
        ----------
        values:
            * Same as for `print`.

        end:
            * String appended at the end of the constructed message.
            * Uses `self.end` if `None`.

        sep:
            * String used to join `values`.
            * Uses `self.sep` if `None`.

        use_repr:
            * Decides how to convert `values` to strings.
            * If `True` uses `repr`.
            * If `False` uses `str`.

        flush:
            * If `True`, call `self.flush` after writing.

        RETURNS
        -------
        Self:
            * The instance.

        """

        if self.enabled:
            self.sep_registry[self.stream] = True
            end = self.end if end is None else end
            sep = self.sep if sep is None else sep
            msg = sep.join(map(repr if use_repr else str, values)) + end

            self.buffer.write(msg)
            if flush:
                self.stream.write(self.buffer.getvalue())
                self.clear_buffer()

        return self
