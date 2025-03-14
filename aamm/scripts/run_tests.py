import traceback
from collections.abc import Callable

import aamm.logging.formats as fmts
import aamm.testing.core as testing
from aamm import file_system as fs
from aamm import metadata
from aamm._.testing import asserts
from aamm.iterable import group_by, split_iter
from aamm.logging import Logger
from aamm.string import indent


def main(
    root: str = None, test_condition: Callable[[testing.Test], bool] = lambda *_: True
) -> int:
    """Run tests and log the results to the standard out."""

    # Run the main test routine. This returns a list of executed tests plus a table of
    # errors encountered during test discovery (if any).
    tests, discovery_errors = testing.main(
        metadata.home if root is None else root, test_condition
    )

    # Count test results.
    total_test_count = len(tests)
    successful_test_count = sum(test.exception is None for test in tests)

    # Make module paths relative to the package's home.
    with fs.cwd_context(metadata.home):
        for test in tests:
            test.module_path = fs.relative(test.module_path)

    # Initialize an stdout logger.
    logger = Logger.from_sys_stream("stdout").separate()

    # Log any discovery errors. These errors occurred not during actual test execution
    # but while discovering and collecting them. This means tests didn't fail because
    # they didn't run in the first place; which is equally as bad.
    if discovery_errors:
        logger.write(fmts.underlined_title("During test discovery"))

        for exception in discovery_errors.values():
            stack = traceback.extract_tb(exception.__traceback__)[4:]
            logger.write(fmts.traceback(stack))

    # Log header.
    logger.write(
        fmts.underlined_title(
            f"Ran {successful_test_count:,}/{total_test_count:,} tests successfully"
        )
    )

    # Group tests based on the module they evaluate.
    for module_path, tests in group_by((t.module_path, t) for t in tests).items():
        successful_tests, failed_tests = split_iter(
            tests, lambda test: test.exception is None
        )

        # Log module line.
        logger.write(
            fmts.contents_table_row(
                fmts.module_identifier(module_path),
                f"{len(successful_tests):,}|{len(tests):,}",
                102,
            )
        )

        # Log failed tests information.
        for suite, tests in group_by((t.suite_name, t) for t in failed_tests).items():
            logger.write(indent(suite))

            for t in tests:
                stack = traceback.extract_tb(t.exception.__traceback__)[1:]

                msg = fmts.traceback(stack, ignore_paths={asserts.__file__})
                msg = indent(msg, 3)

                error_message = fmts.exception_message(t.exception)
                logger.write(indent(f"{t.test_name} -- {error_message}", 2))
                logger.write(msg)

    # Log blank space.
    logger.separate()

    # The exit code of the program should be 0 (everything ok) if all tests passed and
    # there were no discovery errors.
    return int(any(t.exception is not None for t in tests) or bool(discovery_errors))


if __name__ == "__main__":
    import sys

    sys.exit(main())
