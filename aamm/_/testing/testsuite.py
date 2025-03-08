import random
import time
import traceback
from collections.abc import Callable, Hashable
from dataclasses import dataclass
from itertools import chain

from aamm import file_system as fs
from aamm import meta
from aamm.string import right_replace

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

    run: Callable
    module_path: str = ""
    home_path: str = ""
    suite_name: str = ""
    test_name: str = ""
    test_duration: float = None
    exception: Exception = None

    def __lt__(self, other) -> bool:
        a = (self.module_path, self.suite_name, self.test_name)
        b = (other.module_path, other.suite_name, other.test_name)
        return a < b


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
        cls.module_path = is_test_file(cls.home_path)
        if not cls.module_path:
            raise RuntimeError(
                f"{cls.__qualname__} is not instantiated inside a valid test file"
            )

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
    def collect_tests(cls) -> list[Test]:
        """Collect all test symbols in `cls`."""
        storage = []

        for test_name, test in vars(cls).items():
            if callable(test) and test_name.startswith(TEST_PREFIX):
                storage.append(
                    Test(
                        module_path=cls.module_path,
                        home_path=cls.home_path,
                        suite_name=cls.__qualname__,
                        test_name=test_name,
                        run=test,
                    )
                )

        return storage

    @classmethod
    def initialize(cls):
        """Run once before starting tests execution of its respective test suite."""
        pass

    @classmethod
    def run(cls, tests: list[Test]):
        """Call all test symbols in `cls` in a random order and return results data."""

        # Tests are randomly shuffled before execution since they are expected to be
        # completely independent of each other and the order in which they are called.
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

                    # Store failure data.
                    test.exception = exception

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


def is_test_file(path: str) -> str | None:
    """Check whether `path` is a valid test file path."""
    module_path = right_replace(path, TEST_PATH_JOIN, "")
    package_path = fs.join(fs.up(module_path, 2), fs.name(module_path), "__init__.py")

    module_exists = fs.exists(module_path)
    package_exists = fs.exists(package_path)

    if (
        fs.is_file(path)
        and fs.has_extension(path, "py")
        and fs.segment(path, -2) == TEST_DIRECTORY_NAME
        and module_exists ^ package_exists
    ):
        return module_path if module_exists else fs.directory(package_path)


def tag(*tags: tuple[Hashable]) -> Callable:
    """Store `tags` under a `TAGS_ATTRIBUTE` attribute in the decorated test."""

    def decorator(test: Callable) -> Callable:
        setattr(test, TAGS_ATTRIBUTE, frozenset(tags))
        return test

    return decorator


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def collect_tests(
    test_suites: set[TestSuite] = test_suite_registry,
) -> dict[TestSuite, list[Test]]:
    """Generate a dictionary of test-suite: test-list."""
    return {test_suite: test_suite.collect_tests() for test_suite in test_suites}


def discover_tests(root: str) -> list[Exception]:
    """Return a `set` of all `TestSuite` subclasses found in test files under `root`."""
    discovery_errors = []

    for path in fs.search(f"**/{TEST_DIRECTORY_NAME}/*.py", root):
        if is_test_file(path):
            try:
                meta.import_path(path)
            except Exception as e:
                discovery_errors.append(e)

    return discovery_errors


def run_tests(test_collections: dict[TestSuite, list[Test]]) -> list[Test]:
    """Call the `TestSuite.run` method populating tests with result data."""
    for test_suite, tests in test_collections.items():
        test_suite.run(tests)
    return sorted(chain.from_iterable(test_collections.values()))
