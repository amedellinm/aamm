import io
import os.path as path
import sys
import time
import traceback
from collections import namedtuple
from itertools import chain
from random import shuffle
from types import EllipsisType
from typing import Iterator

import aamm.testing.formats as fmts
from aamm.exceptions import qualname
from aamm.file_system import current_file, dir_up
from aamm.std import group_by, split_iter
from aamm.strings import TAB, indent

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


test_suites = []


TestResults = namedtuple(
    "TestResults",
    (
        "package_path",
        "test_path",
        "suite_name",
        "test_name",
        "test_duration",
        "error_name",
        "line_number",
        "error_message",
        "source_code",
    ),
)


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


class TestSuiteMeta(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        test_suites.append(cls)
        cls.home_path = current_file(stack_index=2)


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
    def run(cls) -> list[TestResults]:
        tests = [
            (name, test)
            for name, test in vars(cls).items()
            if (name.startswith("test_") and callable(test))
        ]

        if not tests:
            return []

        shuffle(tests)

        self = cls()
        storage = []

        test_path = cls.home_path
        package_path = dir_up(test_path)
        suite_name = cls.__qualname__

        cls.initialize()

        for test_name, test in tests:
            self.before()

            try:
                t = -time.perf_counter()
                test(self)
                t += time.perf_counter()

            except Exception as exception:
                summary = traceback.extract_tb(exception.__traceback__)[1]
                row = TestResults(
                    package_path=package_path,
                    test_path=test_path,
                    suite_name=suite_name,
                    test_name=test_name,
                    test_duration=None,
                    error_name=qualname(exception),
                    line_number=summary.lineno,
                    error_message=str(exception),
                    source_code=summary.line,
                )

            else:
                row = TestResults(
                    package_path=package_path,
                    test_path=test_path,
                    suite_name=suite_name,
                    test_name=test_name,
                    test_duration=t,
                    error_name=None,
                    line_number=None,
                    error_message=None,
                    source_code=None,
                )

            self.after()

            storage.append(row)

        cls.terminate()

        return storage


test_suites.remove(TestSuite)


# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /


def main(
    stream: io.TextIOWrapper | EllipsisType | None = ...,
    test_suites: list[TestSuite] = test_suites,
) -> None:
    if stream is Ellipsis:
        stream = sys.stdout
    elif stream is None:
        stream = io.StringIO()

    test_info = run_all(test_suites)

    for package_path, test_info in group_by(test_info).items():
        stream.write(f"[ {path.relpath(package_path).replace(path.sep, '.')} ]\n")

        successful_only, mixed = split_iter(
            group_by(test_info).items(),
            lambda item: all(test[2] is not None for test in item[1]),
        )

        for test_path, test_info in successful_only:
            stream.write(
                fmts.module_line(
                    path.basename(test_path),
                    len(test_info),
                    len(test_info),
                    sum(v[2] for v in test_info),
                )
            )

        if successful_only:
            stream.write("\n")

        for test_path, test_info in mixed:
            successful_tests, failed_tests = split_iter(
                test_info, lambda x: x[2] is not None
            )

            stream.write(
                fmts.module_line(
                    path.basename(test_path),
                    len(successful_tests),
                    len(test_info),
                    sum(v[2] for v in successful_tests),
                )
            )

            for suite_name, test_info in group_by(failed_tests).items():
                stream.write(2 * TAB + suite_name + "\n")
                stream.write(
                    "\n".join(
                        indent(fmts.failed_test(test_name, *error_info), 3)
                        for test_name, _, *error_info in test_info
                    )
                )


def run_all(test_suites: list[TestSuite] = test_suites) -> Iterator:
    return chain.from_iterable(test_suite.run() for test_suite in test_suites)
