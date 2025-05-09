import random
import time
import traceback
from collections.abc import Callable, Hashable, Iterator
from dataclasses import dataclass

from aamm import file_system as fs

TAGS_ATTRIBUTE = "aamm-testing-tags"
SUBJECTS_ATTRIBUTE = "aamm-testing-subjects"


@dataclass(slots=True, eq=False)
class Test:
    """A simple data structure to store test information and results."""

    test_suite: "TestSuite"
    test: Callable[["TestSuite"], None]
    exception: Exception = ...
    test_duration: float = float("nan")
    subjects: frozenset[int] = frozenset()
    tags: frozenset = frozenset()

    def __lt__(self, other: "Test") -> bool:
        a = (self.test_suite.home, self.test.__qualname__)
        b = (other.test_suite.home, other.test.__qualname__)
        return a < b


class TestSuite:
    """Main class of the `testing` subpackage."""

    TEST_PREFIX = "test_"

    # Upon declaring a `TestSuite` subclass, a reference to it is saved in this `set`.
    registry: set["TestSuite"] = set()

    def __init_subclass__(cls, *args, **kwargs):
        """Save a reference to every subclass of `TestSuite`."""
        cls.registry.add(cls)
        cls.home = fs.current_file(1)

    @classmethod
    def __iter__(cls) -> Iterator[Callable[["TestSuite"], None]]:
        """Yield all test methods."""
        for name, test in vars(cls).items():
            if callable(test) and name.startswith(cls.TEST_PREFIX):
                yield test

    def after(self):
        """Run after each test in its respective test suite (Even if test failed)."""

    def before(self):
        """Run before each test in its respective test suite."""

    @classmethod
    def count_tests(cls) -> int:
        """Return the number of tests in the suite."""
        return sum(1 for _ in cls())

    @classmethod
    def initialize(cls):
        """Run once before starting tests execution of its respective test suite."""

    @classmethod
    def run(
        cls, test_condition: Callable[[Test], bool] = lambda _: True
    ) -> Iterator[Test]:
        """Call all test symbols in `cls` in a random order and return results data."""

        # Instanciate a `cls` object to run the tests with.
        self = cls()

        tests = []

        for test_method in self:
            # Save test result-independent data.
            test = Test(
                test_suite=cls,
                test=test_method,
                subjects=test_method.__dict__.get(SUBJECTS_ATTRIBUTE, frozenset()),
                tags=test_method.__dict__.get(TAGS_ATTRIBUTE, frozenset()),
            )

            # Filter tests eligible for execution.
            if test_condition(test):
                tests.append(test)

        # Tests are randomly shuffled before execution since they are expected to be
        # independent of each other and the order in which they are run.
        random.shuffle(tests)

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

                    # Traverse the stack looking for the summary corresponding to the
                    # test. This accounts for decorated tests.
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
