import sys
import traceback

import aamm
import aamm.logging.formats as fmts
from aamm import file_system as fs
from aamm._.testing import asserts
from aamm.iterable import group_by, split_iter
from aamm.logging import Logger
from aamm.string import indent
from aamm.testing.core import (
    collect_tests,
    discover_tests,
    run_tests,
    test_suite_registry,
)


def main() -> int:
    logger = Logger.from_sys_stream("stdout")
    logger.separate()

    TAB = "    "

    cwd = fs.cwd()
    fs.cd(root := fs.directory(aamm.__path__[0]))

    discovery_errors = discover_tests(root)

    if discovery_errors:
        header = "During test discovery"
        logger.write(header)
        logger.write(len(header) * "-")

        for exception in discovery_errors:
            stack = traceback.extract_tb(exception.__traceback__)[4:]
            logger.write(fmts.traceback(stack))

    test_collections = collect_tests(test_suite_registry)
    tests = run_tests(test_collections)

    total_count = len(tests)
    favorable_count = sum(test.exception is None for test in tests)

    header = f"Ran {favorable_count:,}/{total_count:,} tests successfully"
    logger.write(header)
    logger.write(len(header) * "-")

    # Group tests based on the module they evaluate.
    for module_path, tests in group_by((t.module_path, t) for t in tests).items():
        successful_tests, failed_tests = split_iter(
            tests, lambda test: test.exception is None
        )

        # Make path relative to `root` for brevity.
        module_path = fs.relative(module_path)

        # Format log message elements.
        logger.write(
            fmts.contents_table_row(
                fs.remove_extension(module_path).replace(fs.SEP, "."),
                f"{len(successful_tests):,}|{len(tests):,}",
                102,
            )
        )

        # Group failed tests based on suite name.
        for suite, tests in group_by((t.suite_name, t) for t in failed_tests).items():
            logger.write(f"{TAB}{suite}")

            for t in tests:
                stack = traceback.extract_tb(t.exception.__traceback__)[1:]

                msg = fmts.traceback(stack, ignore_paths={asserts.__file__})
                msg = indent(msg, 3)

                logger.write(f"{2*TAB}{t.test_name} -- {t.error_message}")
                logger.write(msg)

    logger.separate()

    # Resume CWD.
    fs.cd(cwd)

    # If the number of successful tests is equal to the total number of tests, then the
    # exit code of the program should be 0 (everything ok).
    return int(bool(discovery_errors) or total_count != favorable_count)


if __name__ == "__main__":
    sys.exit(main())
