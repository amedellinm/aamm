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

    @testing.subjects(
        meta.DictTrackUnused.__getitem__,
        meta.DictTrackUnused.__init__,
        meta.DictTrackUnused.__setitem__,
        meta.DictTrackUnused.unused_keys,
    )
    def test_dict_track_unused(self):
        dictionary = meta.DictTrackUnused({"a": 1, "b": 2})
        asserts.equal({"a", "b"}, dictionary.unused_keys())

        dictionary["a"]
        asserts.equal({"b"}, dictionary.unused_keys())

        dictionary["c"] = 3
        asserts.equal({"b", "c"}, dictionary.unused_keys())

    @testing.subjects(meta.import_path)
    def test_import_path(self):
        """
        `meta.import_path` is heavily used in the internals of the `aamm.testing`
        subpackage. No test I could write here would be more rigorous than straight-up
        using the machinery to run this very test.

        """

    @testing.subjects(meta.mangle)
    def test_mangle(self):
        class A:
            pass

        class _B:
            pass

        a = A()
        b = _B()

        asserts.equal(meta.mangle(a, "name"), "_A__name")
        asserts.equal(meta.mangle(b, "name"), "_B__name")

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
            a = None
            b = None

        asserts.equal(sorted(dict(namespace.unused_names())), ["a", "b"])
        namespace.b
        asserts.equal(sorted(dict(namespace.unused_names())), ["a"])
        namespace.a
        asserts.equal(sorted(dict(namespace.unused_names())), [])

    @testing.subjects(meta.public_members)
    def test_public_members(self):
        class A:
            class_variable = 1

            def __hash__(self):
                pass

            def _method(self):
                pass

            @classmethod
            def class_method(cls):
                pass

        class B(A):
            def __init__(self):
                pass

            def method(self):
                pass

        obtained_names, obtained_objects, obtained_types = zip(*meta.public_members(B))

        expected_names = [
            "TestMeta.test_public_members.<locals>.A.__hash__",
            "TestMeta.test_public_members.<locals>.B.__init__",
            "TestMeta.test_public_members.<locals>.A.class_method.__func__",
            "TestMeta.test_public_members.<locals>.A.class_variable",
            "TestMeta.test_public_members.<locals>.B.method",
        ]

        for expected, obtained in zip(expected_names, obtained_names):
            asserts.equal(expected, obtained)

        expected_objects = [
            A.__hash__,
            B.__init__,
            A.class_method.__func__,
            A.class_variable,
            B.method,
        ]

        for expected, obtained in zip(expected_objects, obtained_objects):
            asserts.equal(expected, obtained)

        expected_types = [A, B, A, A, B]

        for expected, obtained in zip(expected_types, obtained_types):
            asserts.equal(expected, obtained)

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
