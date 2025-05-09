import io
import os
import sys
from collections import deque
from threading import Lock
from typing import Any, Literal, TextIO
from weakref import finalize

from aamm import file_system as fs
from aamm import meta

try:
    from typing import Self
except ImportError:
    from typing import Any as Self


class Logger:
    """
    DESCRIPTION
    -----------
    A logger is essentially just an IO stream.

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

    SEP = " "
    END = "\n"
    FLUSH = True

    sep_registry = {}

    unmanaged = meta.ReadOnlyProperty()

    def __init__(
        self, stream: TextIO, enabled: bool = True, unmanaged: bool = False
    ) -> None:
        self.stream = stream
        self.enabled = enabled
        self.unmanaged = unmanaged

        self.__lock = Lock()
        self.__buffer = io.StringIO()
        self.__write_history = deque([], maxlen=50)
        self.sep_registry.setdefault(stream, True)

        if not unmanaged:
            finalize(self, self.stream.close)

    def __repr__(self) -> str:
        return f"{type(self).__qualname__}(stream={self.stream}, enabled={self.enabled}, unmanaged={self.unmanaged})"

    def clear_buffer(self) -> Self:
        """Clear buffer."""
        with self.__lock:
            self.__buffer.seek(0)
            self.__buffer.truncate()
            self.__write_history.clear()
        return self

    def clear_stream(self) -> Self:
        """Clear stream."""
        with self.__lock:
            self.stream.seek(0)
            self.stream.truncate()
        return self

    def flush(self) -> Self:
        """Dump buffer to `self.stream` though `self.write`."""
        return self.write(end="", flush=True)

    @classmethod
    def from_current_file(cls, mode: str = "a", stack_index: int = 0) -> Self:
        """
        Construct a `cls` instance using a stream that points to the file defined
        by joining the path segments:
            * The directory where the caller's source file lives
            * A folder named `cls.DIR_NAME`
            * A .log file of the same name as the caller's source file

        """
        file = fs.current_file(stack_index + 1)
        logs = fs.with_leaf(file, cls.DIR_NAME)
        os.makedirs(logs, exist_ok=True)
        path = fs.join(logs, fs.with_extension(fs.leaf(file), "log"))
        return cls(open(path, mode))

    @classmethod
    def from_string_io(cls) -> Self:
        """Use a `io.StringIO` to construct `cls`."""
        return cls(io.StringIO())

    @classmethod
    def from_sys_stream(
        cls, stream_name: Literal["stdout", "stderr"] = "stdout"
    ) -> Self:
        """Construct a `Logger` instance using a stream from the `sys` module."""
        if stream_name in ("stdout", "stderr"):
            return cls(getattr(sys, stream_name), unmanaged=True)
        raise ValueError(f"expected 'stdout' or 'stderr', got {stream_name!r}")

    def separate(
        self, multiplier: int = 2, flush: bool = None, forced: bool = False
    ) -> Self:
        """Log `multiplier * self.END` idempotently."""
        with self.__lock:
            if not (self.sep_registry[self.stream] or forced):
                return

        self.write(end=multiplier * self.END, flush=flush)

        with self.__lock:
            self.sep_registry[self.stream] = False

        return self

    def undo(self, actions: int = 1, ignore_empty: bool = True) -> Self:
        """Undo the last n actions. Only works if the actions were not flushed."""
        with self.__lock:
            if self.__write_history or not ignore_empty:
                n = sum(self.__write_history.pop() for _ in range(actions))
                self.__buffer.seek(self.__buffer.tell() - n)
                self.__buffer.truncate()

        return self

    def write(
        self,
        *values: tuple[Any],
        end: str = None,
        sep: str = None,
        flush: int = None,
    ) -> Self:
        """
        DESCRIPTION
        -----------
        This is the main method of the class. It provides a `print`-like interface for
        logging.

        PARAMETERS
        ----------
        values:
            * Same as for `print`.

        end:
            * String appended at the end of the constructed message.
            * Uses `self.END` if `None`.

        sep:
            * String used to join `values`.
            * Uses `self.SEP` if `None`.

        flush:
            * If `True`, call `self.FLUSH` after writing.

        RETURNS
        -------
        Self:
            * The instance.

        """

        if self.enabled:
            end = self.END if end is None else end
            sep = self.SEP if sep is None else sep
            flush = self.FLUSH if flush is None else flush

            msg = sep.join(map(str, values)) + end

            with self.__lock:
                self.sep_registry[self.stream] = True
                n = self.__buffer.write(msg)

                if flush:
                    self.stream.write(self.__buffer.getvalue())
                    self.__buffer.seek(0)
                    self.__buffer.truncate()
                    self.__write_history.clear()
                else:
                    self.__write_history.append(n)

        return self
