import io
import sys

from aamm import meta
from aamm.testing import TestSuite, asserts


class TestMeta(TestSuite):
    def test_capture_stdout(self):
        message = "Hello World"

        with meta.capture_stdout(stream := io.StringIO()):
            print(message, end="")
            asserts.identical(stream, sys.stdout)

        asserts.not_identical(stream, sys.stdout)
        asserts.equal(message, stream.getvalue())

    def test_constant_boolean_operations(self):
        everything = meta.ConstantBooleanOperations({"__contains__": True})
        asserts.contain(everything, "a")
        asserts.contain(everything, 0)
        asserts.contain(everything, None)
        asserts.contain(everything, ...)

        infinity = meta.ConstantBooleanOperations({"__gt__": True})
        asserts.greater_than(infinity, "a")
        asserts.greater_than(infinity, ...)
        asserts.greater_than(infinity, None)
        asserts.greater_than(infinity, 1_000_000_000_000)

    def test_import_path(self):
        """
        `meta.import_path` is heavily used in the internals of the `aamm.testing`
        subpackage. No test I could write here would be more rigorous than straight-up
        using the machinery to run this very test.

        """

    def test_namespace(self):
        class namespace(metaclass=meta.Namespace):
            bla = None

        namespace.bla = 10

        with asserts.exception_context(AttributeError):
            namespace.ble = 10

    def test_namespace_track_unused(self):
        class namespace(metaclass=meta.NamespaceTrackUnused):
            b = 2
            a = 1

        asserts.equal(namespace._unused_names(), ["a", "b"])
        namespace.b
        asserts.equal(namespace._unused_names(), ["a"])
        namespace.a
        asserts.equal(namespace._unused_names(), [])

    def test_read_only_property(self):
        class A:
            x = meta.ReadOnlyProperty()

        with asserts.exception_context(AttributeError):
            A.x

        a = A()
        a.x = 0

        with asserts.exception_context(AttributeError):
            a.x = 1

    def test_typehint_handlers(self):
        handler = meta.typehint_handlers(
            {str | list[str]: lambda arg: [arg] if isinstance(arg, str) else arg}
        )

        @handler
        def f(x: str | list[str]) -> list[str]:
            return x

        asserts.equal(["a"], f("a"))
        asserts.equal(["a"], f(["a"]))
