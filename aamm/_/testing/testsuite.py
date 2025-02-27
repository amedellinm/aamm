import random
import time
import traceback
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from itertools import chain

from aamm import file_system as fs
from aamm import meta
from aamm.strings import right_replace

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


TEST_DIRECTORY_NAME = "__tests"
TEST_PREFIX = "test_"

# Some shorthands.
TEST_PATH_JOIN = f"{TEST_DIRECTORY_NAME}{fs.SEP}"
TEST_MODULE_JOIN = f"{TEST_DIRECTORY_NAME}."

# When tests are decorated using the `tag` function, they are given an attribute called
# `TAGS_ATTRIBUTE` with a `set` of tags as its value.
TAGS_ATTRIBUTE = "testing-tags"


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


@dataclass(slots=True)
class Test:
    """A simple data structure to store test information and results."""

    module_path: str
    suite_name: str
    test_name: str
    run: Callable
    test_duration: float = None
    where: str = None
    error_name: str = None
    error_message: str = None

    def __lt__(self, other) -> bool:
        a = (self.module_path, self.suite_name, self.test_name)
        b = (other.module_path, other.suite_name, other.test_name)
        return a < b

    def __str__(self) -> str:
        return (
            f"module_path: {self.module_path}\n"
            f"suite_name: {self.suite_name}\n"
            f"test_name: {self.test_name}\n"
            f"test_duration: {1000*self.test_duration:.3f} ms\n"
            f"where: {self.where}\n"
            f"error_name: {self.error_name}\n"
            f"error_message: {self.error_message}"
        )


class TestSuiteMeta(type):
    def __init__(cls, *args):
        super().__init__(*args)

        # The `TestSuite` class is a special case only meant for inheritance. It does
        # it does not contain tests, so the logic after this condition shouldn't be
        # executed.

        if cls.__name__ == "TestSuite":
            return

        cls.home_path = fs.current_file(stack_index=1)

        # To enforce good practices, an exception is thrown if a test suite is declared
        # in a file with an unexpected path format.
        if not is_test_file(cls.home_path):
            raise RuntimeError(
                f"{cls.__qualname__} is not instantiated inside a valid test file"
            )

        cls.module_path = right_replace(cls.home_path, TEST_PATH_JOIN, "")

        test_suite_registry.add(cls)


# Upon declaring a `TestSuite` subclass, a reference to it is saved in this `set`.
test_suite_registry: set[TestSuiteMeta] = set()


class FakeTestSuite:
    """Main class of the `testing` subpackage."""

    home_path = None
    module_path = None

    def after(self):
        """Run after each test in its respective test suite (Even if test failed)."""
        pass

    def before(self):
        """Run before each test in its respective test suite."""
        pass

    @classmethod
    def collect_tests(cls) -> tuple[TestSuiteMeta, list[Test]]:
        """Collect all test symbols in `cls`."""
        storage = []

        for test_name, test in vars(cls).items():
            if callable(test) and test_name.startswith(TEST_PREFIX):
                storage.append(
                    Test(
                        module_path=cls.module_path,
                        suite_name=cls.__qualname__,
                        test_name=test_name,
                        run=test,
                    )
                )

        return cls, storage

    @classmethod
    def initialize(cls):
        """Run once before starting tests execution of its respective test suite."""
        pass

    @classmethod
    def run(cls, tests: list[Test], seed: int = None):
        """Call all test symbols in `cls` in a random order and return results data."""

        # Tests are randomly shuffled before execution since they are expected to be
        # completely independent of each other and the order in which they are called.
        random.seed(seed)
        random.shuffle(tests)

        # Instanciate a `cls` object to run the tests with.
        self = cls()

        cls.initialize()

        try:
            for test in tests:
                self.before()

                try:
                    # Time and run the test.
                    t = time.perf_counter()
                    test.run(self)

                except Exception as exception:
                    stack = traceback.extract_tb(exception.__traceback__)

                    for summary in stack:
                        if summary.name == test.run.__name__:
                            break
                    else:
                        summary = stack[-1]

                    # Store failure data.
                    test.where = f"{summary.lineno}:{summary.colno}"
                    test.error_name = type(exception).__qualname__
                    test.error_message = str(exception)

                finally:
                    self.after()

                test.test_duration = time.perf_counter() - t

        finally:
            cls.terminate()

    @classmethod
    def terminate(cls):
        """Run once after all tests in its respective test suite were executed."""
        pass


class TestSuite(FakeTestSuite, metaclass=TestSuiteMeta):
    pass


def get_tags(test: Callable) -> frozenset:
    """Extract tags from test."""
    return test.run.__dict__.get(TAGS_ATTRIBUTE, frozenset())


def is_test_file(path: str) -> bool:
    """Check whether `path` is a valid test file path."""
    module_path = right_replace(path, TEST_PATH_JOIN, "")
    package_path = fs.remove_extension(module_path) + fs.SEP + "__init__.py"

    return all(
        (
            fs.is_file(path),
            fs.has_extension(path, "py"),
            fs.segment(path, -2) == TEST_DIRECTORY_NAME,
            fs.exists(module_path) or fs.exists(package_path),
        )
    )


def tag(*tags: tuple[Hashable]) -> Callable:
    """Store `tags` under a `TAGS_ATTRIBUTE` attribute in the decorated test."""

    def decorator(test: Callable) -> Callable:
        setattr(test, TAGS_ATTRIBUTE, frozenset(tags))
        return test

    return decorator


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def collect_tests(
    test_suites: set[TestSuiteMeta] = test_suite_registry,
) -> dict[TestSuiteMeta, list[Test]]:
    """Generate a dictionary of test-suite: test-list."""
    return dict(test_suite.collect_tests() for test_suite in test_suites)


def discover_tests(root: str) -> set[TestSuiteMeta]:
    """Return a `set` of all `TestSuite` subclasses found in test files under `root`."""
    for path in fs.search(root, f"**/{TEST_DIRECTORY_NAME}/*.py"):
        if is_test_file(path):
            meta.import_path(path)

    return test_suite_registry.copy()


def main(root: str, seed: int = None) -> list[Test]:
    """Run a basic testing routine and return a list of executed tests."""
    test_suites = discover_tests(root)
    test_collections = collect_tests(test_suites)
    run_tests(test_collections, seed=seed)
    return sorted(chain.from_iterable(test_collections.values()))


def run_tests(test_collections: dict[TestSuiteMeta, list[Test]], seed=None):
    """Call the `TestSuiteMeta.run` method populating tests with result data."""
    for test_suite, tests in test_collections.items():
        test_suite.run(tests, seed)
