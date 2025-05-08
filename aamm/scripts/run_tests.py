import traceback
from collections.abc import Callable
from importlib import import_module
from itertools import chain

import aamm.logging.formats as fmts
from aamm import file_system as fs
from aamm import meta, metadata, testing
from aamm._.testing import asserts
from aamm.iterable import group_by
from aamm.logging import Logger
from aamm.strings import indent
from aamm.testing import Test


def main(test_condition: Callable[[Test], bool] = lambda *_: True) -> int:
    """Run tests and log the results to the standard out."""

    logger = Logger.from_sys_stream("stdout")
    logger.separate()

    # Discover tests.
    discovery_errors = {}

    for path in metadata.test_files:
        module = meta.module_name(fs.relative(path, metadata.home))
        try:
            # Importing a file containing subclasses of `testing.TestSuit` loads
            # them to `testing.TestSuit.registry`.
            import_module(module)
        except Exception as e:
            # Save discovery error.
            discovery_errors[path] = e

    # Log header.
    test_count = sum(ts.count_tests() for ts in testing.TestSuite.registry)
    logger.write(
        fmts.underlined_title(f"Running {test_count} test{'s'*bool(test_count)}")
    )

    tests = []

    # Group test suites by module path.
    module_groups: dict[str, tuple[testing.TestSuite]] = group_by(
        (fs.relative(ts.home, metadata.home), ts) for ts in testing.TestSuite.registry
    )

    for module_path, test_suites in sorted(module_groups.items()):
        # Log module info.
        module_name = meta.module_name(module_path)
        test_count = sum(ts.count_tests() for ts in test_suites)
        logger.write(module_name, f"({test_count:,})")

        for name, test_suite in sorted((ts.__qualname__, ts) for ts in test_suites):
            # Log test suite info.
            logger.write(f"    {name} ({test_suite.count_tests():,})")

            for test in test_suite.run(test_condition):
                tests.append(test)

                # Log test info.
                test_name = test.test.__name__
                time = test.test_duration * 1_000
                logger.write(
                    indent(fmts.contents_table_row(test_name, f"{time:,.3f} ms"), 2),
                    "  *" * (test.exception is not None),
                )

                if test.exception is None:
                    continue

                # Extract the traceback without the test runner frame.
                stack = traceback.extract_tb(test.exception.__traceback__)[1:]

                msg = fmts.traceback(stack, ignore_paths={asserts.__file__})
                msg = indent(msg, 4)
                error_message = fmts.exception_message(test.exception)

                # Log error info.
                logger.write(indent(error_message, 3))
                logger.write(msg)

                logger.separate(1, flush=False)

            logger.undo(ignore_empty=True)
            logger.separate(1, flush=False, forced=True)

    logger.undo(ignore_empty=True)
    logger.separate(forced=True)

    # Log any discovery errors. These errors occurred not during actual test execution
    # but while discovering and collecting them. This means tests didn't fail because
    # they didn't run in the first place; which is equally as bad.
    if discovery_errors:
        logger.write(fmts.underlined_title("During test discovery"))

        for exception in discovery_errors.values():
            # Index 4 skips `testing` stack frames.
            stack = traceback.extract_tb(exception.__traceback__)[4:]
            logger.write(fmts.exception_message(exception))
            logger.write(indent(fmts.traceback(stack)))
            logger.separate(1)

        logger.separate(1, forced=True)

    # Track untested symbols.
    tested_symbols = set(chain.from_iterable(test.subjects for test in tests))
    untested_symbols = tuple(
        symbol_info
        for symbol_id, symbol_info in metadata.api_symbols().items()
        if symbol_id not in tested_symbols
        and symbol_info.source_file is not None
        and not isinstance(symbol_info.value, type)
    )

    if untested_symbols:
        # Log all symbols missing inside `testing.subjects` decorators.
        logger.write(
            fmts.underlined_title(
                "Missing TESTS for the following public symbols "
                f"({len(untested_symbols):,})"
            )
        )

        # Group symbols by header file.
        header_file_groups: dict[str, tuple[metadata.SymbolInfo]] = group_by(
            (fs.relative(si.header_file, metadata.home), si) for si in untested_symbols
        )

        for header_file, symbols_info in header_file_groups.items():
            # Log symbol info.
            logger.write(f"{header_file} ({len(symbols_info)})")
            for symbol_info in symbols_info:
                logger.write("  -", symbol_info.name)

            logger.separate(1)

        logger.separate(1, forced=True)

    # The exit code of the program should be 0 (everything ok) if all tests passed,
    # there were no discovery errors and all symbols were tested.
    return int(
        any(t.exception is not None for t in tests)
        or bool(discovery_errors)
        or bool(untested_symbols)
    )


if __name__ == "__main__":
    import sys

    sys.exit(main())
