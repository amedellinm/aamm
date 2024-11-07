import time
import traceback
from collections import namedtuple
from itertools import chain
from random import shuffle
from typing import Callable, Iterator

from aamm import file_system as fs
from aamm import std

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


TEST_PREFIX = "test_"

test_suites = []

TestResult = namedtuple(
    "TestResult",
    (
        "test_path",
        "suite_name",
        "test_name",
        "test_duration",
        "where",
        "error_name",
        "error_message",
    ),
)


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


class TestSuiteMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        test_suites.append(cls)
        cls.home_path = fs.current_file(stack_index=1)


class TestSuite(metaclass=TestSuiteMeta):
    def after(self):
        pass

    def before(self):
        pass

    @classmethod
    def initialize(self):
        pass

    @classmethod
    def terminate(self):
        pass

    @classmethod
    def run(cls) -> list[TestResult]:
        """Call all test methods in `cls` in a random order and return results data."""

        # Get all tests defined in the test suite. These are all members of `cls` that
        # are callable and with a name matching the test-naming schema.
        tests = [
            (name, test)
            for name, test in vars(cls).items()
            if (name.startswith("test_") and callable(test))
        ]

        # Return an empty list if there are no tests defined.
        if not tests:
            return []

        # Tests are randomly shuffled before execution since they are expected to be
        # completely independent of each other and the order in which they are called.
        shuffle(tests)

        # Some of the data of the tests that belong to the same suite is constant, so
        # it is computed outside the loop.
        constant_data = (cls.home_path, cls.__qualname__)

        # Instanciate a `TestSuite` object to run the tests.
        self = cls()

        # This is the returned structure with all the `TestResult` objects.
        storage = []

        cls.initialize()

        for test_name, test in tests:
            # Ignore all tests marked with the skip decorator.
            if hasattr(test, "aamm.testing-skip_test"):
                continue

            variable_data = [test_name, None, None, None, None]

            self.before()

            try:
                # Time and run the test.
                t = -time.perf_counter()
                test(self)
                t += time.perf_counter()

            except Exception as exception:
                # Store failure data.
                stack = traceback.extract_tb(exception.__traceback__)
                summary = stack[len(stack) != 1]
                variable_data[2:] = (
                    f"{summary.lineno}:{summary.colno}",
                    std.qualname(exception),
                    str(exception),
                )

            else:
                # If successful, the test duration is stored.
                variable_data[1] = t

            self.after()

            # Store test result.
            storage.append(TestResult(*constant_data, *variable_data))

        cls.terminate()

        return storage


test_suites.remove(TestSuite)


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def run_all(test_suites: list[TestSuite] = test_suites) -> Iterator[TestResult]:
    return chain.from_iterable(test_suite.run() for test_suite in test_suites)


def main():
    """TODO"""


def skip(test: Callable):
    setattr(test, "aamm.testing-skip_test", None)
    return test
