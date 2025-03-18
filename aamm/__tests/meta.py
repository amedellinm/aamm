import io
import sys

from aamm import file_system as fs
from aamm import meta, testing
from aamm.testing import asserts


class TestMeta(testing.TestSuite):
    @testing.subjects(meta.capture_stdout)
    def test_capture_stdout(self):
        message = "Hello World"

        with meta.capture_stdout(stream := io.StringIO()):
            print(message, end="")
            asserts.identical(stream, sys.stdout)

        asserts.not_identical(stream, sys.stdout)
        asserts.equal(message, stream.getvalue())

    @testing.subjects(meta.ConstantBooleanOperations)
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

    @testing.subjects(meta.import_path)
    def test_import_path(self):
        """
        `meta.import_path` is heavily used in the internals of the `aamm.testing`
        subpackage. No test I could write here would be more rigorous than straight-up
        using the machinery to run this very test.

        """

    @testing.subjects(meta.module_identifier)
    def test_module_identifier(self):
        path = fs.join("a", "b", "c.py")
        module = "a.b.c"
        asserts.equal(module, meta.module_identifier(path))

        path = fs.join("a", "b", "__init__.py")
        module = "a.b"
        asserts.equal(module, meta.module_identifier(path))

    @testing.subjects(meta.Namespace)
    def test_namespace(self):
        class namespace(metaclass=meta.Namespace):
            bla = None

        namespace.bla = 10

        with asserts.exception_context(AttributeError):
            namespace.ble = 10

    @testing.subjects(meta.NamespaceTrackUnused)
    def test_namespace_track_unused(self):
        class namespace(metaclass=meta.NamespaceTrackUnused):
            b = 2
            a = 1

        asserts.equal(namespace._unused_names(), ["a", "b"])
        namespace.b
        asserts.equal(namespace._unused_names(), ["a"])
        namespace.a
        asserts.equal(namespace._unused_names(), [])

    @testing.subjects(
        meta.ReadOnlyProperty,
        meta.ReadOnlyProperty.__get__,
        meta.ReadOnlyProperty.__set__,
        meta.ReadOnlyProperty.__set_name__,
    )
    def test_read_only_property(self):
        class A:
            x = meta.ReadOnlyProperty()

        a = A()
        a.x = 0

        with asserts.exception_context(AttributeError):
            a.x = 1

        assert isinstance(A.x, meta.ReadOnlyProperty)
        assert isinstance(a.x, int)
        asserts.equal(a.x, a._x)

    @testing.subjects(meta.typehint_handlers)
    def test_typehint_handlers(self):
        handler = meta.typehint_handlers(
            {str | list[str]: lambda arg: [arg] if isinstance(arg, str) else arg}
        )

        @handler
        def f(x: str | list[str]) -> list[str]:
            return x

        asserts.equal(["a"], f("a"))
        asserts.equal(["a"], f(["a"]))
