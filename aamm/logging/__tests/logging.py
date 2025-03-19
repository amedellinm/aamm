import sys

from aamm import testing
from aamm.logging import Logger
from aamm.testing import asserts


class TestLogger(testing.TestSuite):
    @testing.subjects(Logger.clear_buffer, Logger.flush)
    def test_clear_buffer(self):
        logger = Logger.from_string_io().write(message := "Hello World", end="")
        logger.write("!", flush=False)
        logger.clear_buffer()
        logger.flush()
        asserts.equal(message, logger.stream.getvalue())

    @testing.subjects(Logger.clear_stream)
    def test_clear_stream(self):
        logger = Logger.from_string_io().write("Hello World", end="")
        logger.clear_stream()
        asserts.equal("", logger.stream.getvalue())

    @testing.subjects(Logger.from_string_io.__func__, Logger.END, Logger.SEP)
    def test_constants(self):
        logger = Logger.from_string_io()
        logger.SEP = "sep"
        logger.END = "end"
        logger.write("A", "B", "C")
        asserts.equal(logger.stream.getvalue(), "AsepBsepCend")

    @testing.subjects(Logger.FLUSH)
    def test_flush(self):
        logger = Logger.from_string_io()
        logger.FLUSH = False
        logger.write("a")
        logger.write("b")
        logger.write("c")
        asserts.false(logger.stream.getvalue())

    @testing.subjects(Logger.from_sys_stream.__func__)
    def test_from_sys_stream(self):
        asserts.identical(sys.stdout, Logger.from_sys_stream().stream)
        asserts.identical(sys.stdout, Logger.from_sys_stream("stdout").stream)
        asserts.identical(sys.stderr, Logger.from_sys_stream("stderr").stream)

    @testing.subjects(Logger.undo)
    def test_undo(self):
        logger = Logger.from_string_io()
        logger.write("qwerty", flush=False, end="")
        logger.write("azerty", flush=False, end="")
        logger.write("123456", flush=False, end="")
        logger.undo(2)
        asserts.equal(logger.stream.getvalue(), "")

        logger.flush()
        asserts.equal(logger.stream.getvalue(), "qwerty")

    @testing.subjects(Logger.write)
    def test_write(self):
        logger = Logger.from_string_io()
        logger.write("Hello", "world", end=";", flush=False)

        assert not logger.stream.getvalue()

        logger.flush()
        asserts.equal("Hello world;", logger.stream.getvalue())

        logger.clear_stream()
        logger.write(1, 2, 3, 4, end="")
        asserts.equal("1 2 3 4", logger.stream.getvalue())
