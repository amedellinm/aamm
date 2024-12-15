import io
from contextlib import contextmanager
from types import EllipsisType
from typing import Any, Self, TextIO
from weakref import finalize

import aamm.logtools.formats as fmt
from aamm.meta import ReadOnlyProperty


class Logger:
    sep = " "
    end = "\n"
    sep_registry = {}

    unmanaged = ReadOnlyProperty()

    def __init__(
        self,
        stream: TextIO | EllipsisType,
        enabled: bool = True,
        unmanaged: bool = False,
    ) -> None:
        self.stream = stream
        self.enabled = enabled
        self.unmanaged = unmanaged

        self.callbacks = []
        self.buffer = io.StringIO()
        self.sep_registry.setdefault(stream, True)

        if not unmanaged:
            finalize(self, self.stream.close)

        finalize(self, self._final_dispatch)

    def __repr__(self) -> str:
        return fmt.reprlike(self, "stream", "enabled", "unmanaged")

    def _final_dispatch(self) -> None:
        """Run all callbacks in `self.callbacks` upon instance destruction."""
        for callback, args, kwargs in self.callbacks:
            callback(*args, **kwargs)

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
        """Dump `self.buffer` to `self.stream`."""
        self.stream.write(self.buffer.getvalue())
        return self.clear_buffer()

    @contextmanager
    def isolate(self, multiplier_enter: int = 2, multiplier_exit: int = 2):
        """Run the `separate` method before and after the context."""
        self.separate(multiplier_enter)
        yield
        self.separate(multiplier_exit)

    def separate(self, multiplier: int = 2) -> Self:
        """Log `multiplier * self.end` idempotently."""
        if self.sep_registry[self.stream]:
            self.write("", sep="", end=multiplier * self.end)
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
                self.flush()

        return self
