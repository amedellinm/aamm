import random
import time
import traceback
from collections.abc import Callable, Hashable, Iterator
from dataclasses import dataclass
from itertools import chain

from aamm import file_system as fs
from aamm import meta
from aamm.string import right_replace

TEST_DIRECTORY_NAME = "__tests"
TEST_PREFIX = "test_"
TEST_PATH_JOIN = f"{TEST_DIRECTORY_NAME}{fs.SEP}"
TAGS_ATTRIBUTE = "aamm-testing-tags"
SUBJECTS_ATTRIBUTE = "aamm-testing-subjects"


@dataclass(slots=True, eq=False)
class Test:
    """A simple data structure to store test information and results."""

    test_suite: "TestSuite" = None
    test: Callable[["TestSuite"], None] = None
    exception: Exception = ...
    test_duration: float = float("nan")
    subjects: frozenset[int] = frozenset()
    tags: frozenset = frozenset()


class TestSuite:
    """Main class of the `testing` subpackage."""

    # Upon declaring a `TestSuite` subclass, a reference to it is saved in this `set`.
    registry: set["TestSuite"] = set()

    def __init_subclass__(cls, *args, **kwargs):
        """Save a reference to every subclass of `TestSuite`."""
        super().__init_subclass__(*args, **kwargs)
        cls.registry.add(cls)
        cls.module_path = is_test_file(fs.current_file(1))

    def after(self):
        """Run after each test in its respective test suite (Even if test failed)."""
        pass

    def before(self):
        """Run before each test in its respective test suite."""
        pass

    @classmethod
    def count_tests(cls) -> int:
        """Return the number of tests in the suite."""
        return sum(
            1
            for test_name, test in vars(cls).items()
            if callable(test) and test_name.startswith(TEST_PREFIX)
        )

    @classmethod
    def initialize(cls):
        """Run once before starting tests execution of its respective test suite."""
        pass

    @classmethod
    def run(
        cls, test_condition: Callable[[Test], bool] = lambda _: True
    ) -> Iterator[Test]:
        """Call all test symbols in `cls` in a random order and return results data."""

        # Instanciate a `cls` object to run the tests with.
        self = cls()

        tests = list(
            filter(
                test_condition,
                (
                    Test(
                        test_suite=cls,
                        test=test,
                        subjects=test.__dict__.get(SUBJECTS_ATTRIBUTE, frozenset()),
                        tags=test.__dict__.get(TAGS_ATTRIBUTE, frozenset()),
                    )
                    for name, test in vars(cls).items()
                    if callable(test) and name.startswith(TEST_PREFIX)
                ),
            )
        )

        # Tests are randomly shuffled before execution since they are expected to be
        # independent of each other and the order in which they are run.
        # random.shuffle(tests)

        cls.initialize()

        try:
            for test in tests:
                self.before()

                try:
                    # Time and run the test.
                    t = time.perf_counter()
                    test.test(self)

                except Exception as exception:
                    stack = traceback.extract_tb(exception.__traceback__)

                    for summary in stack:
                        if summary.name == test.test.__name__:
                            break

                    # Store failure data.
                    test.exception = exception

                else:
                    # If there was no exception, set the field to `None`.
                    test.exception = None

                finally:
                    self.after()

                test.test_duration = time.perf_counter() - t

                yield test

        finally:
            cls.terminate()

    @classmethod
    def terminate(cls):
        """Run once after all tests in its respective test suite were executed."""
        pass


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


def subjects(*subjects: tuple) -> Callable:
    """Store `subjects` under a `SUBJECTS_ATTRIBUTE` attribute in the decorated test."""

    def decorator(test: Callable) -> Callable:
        setattr(test, SUBJECTS_ATTRIBUTE, frozenset(map(id, subjects)))
        return test

    return decorator


def tag(*tags: tuple[Hashable]) -> Callable:
    """Store `tags` under a `TAGS_ATTRIBUTE` attribute in the decorated test."""

    def decorator(test: Callable) -> Callable:
        setattr(test, TAGS_ATTRIBUTE, frozenset(tags))
        return test

    return decorator


def test_file(path: str) -> str:
    """Return the proper path to the test file corresponding to `path`."""
    leaf = (
        fs.name(fs.directory(path)) + ".py"
        if fs.leaf(path) == "__init__.py"
        else fs.leaf(path)
    )
    return fs.with_leaf(path, TEST_PATH_JOIN + leaf)


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def main(
    root: str, test_condition: Callable[[Test], bool]
) -> tuple[list[Test], dict[str, Exception]]:
    """Discover, collect, filter, and run tests found under `root`."""

    discovery_errors = {}

    for path in fs.glob(f"**/{TEST_DIRECTORY_NAME}/*.py", root, with_root=True):
        if is_test_file(path):
            try:
                meta.import_path(path)
            except Exception as e:
                discovery_errors[path] = e

    tests = sorted(
        chain.from_iterable(
            test_suite.run(test_condition) for test_suite in TestSuite.registry
        )
    )

    return tests, discovery_errors
