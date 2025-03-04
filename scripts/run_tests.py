import sys

from aamm import file_system as fs
from aamm import testing
from aamm.iterable import group_by, split_iter
from aamm.logging import Logger
from aamm.logging.formats import contents_table_row


def main() -> int:
    logger = Logger.from_sys_stream("stdout")

    LINES_AROUND = 3
    TAB = "    "

    root = fs.cwd()
    tests = testing.main(root)

    total_count = len(tests)
    favorable_count = sum(test.exception is None for test in tests)

    header = f"Ran {favorable_count:,}/{total_count:,} tests successfully"
    logger.separate()
    logger.write(header)
    logger.write(len(header) * "-")

    # Group tests based on the module they evaluate.
    for module_path, tests in group_by((t.module_path, t) for t in tests).items():
        successful_tests, failed_tests = split_iter(
            tests, lambda test: test.exception is None
        )

        # Make path relative to `root` for brevity.
        module_path = module_path.removeprefix(root + fs.SEP)

        # Format log message elements.
        logger.write(
            contents_table_row(
                fs.remove_extension(module_path).replace(fs.SEP, "."),
                f"{len(successful_tests):,}|{len(tests):,}",
                102,
            )
        )

        # Group failed tests based on suite name.
        for suite, tests in group_by((t.suite_name, t) for t in failed_tests).items():
            logger.write(f"{TAB}{suite}")

            for t in tests:
                logger.write(f"{2*TAB}{t.test_name} -- {t.error_message}")

                # Compute padding so that line numbers are aligned
                padding = len(
                    str(max(f.lineno for f in t.traceback_stack) + LINES_AROUND)
                )

                for frame in t.traceback_stack:
                    # Make path relative to `root` for brevity.
                    filename = fs.resolve(frame.filename).removeprefix(root + fs.SEP)
                    logger.write(f"{3*TAB}{filename}  ({frame.name})")

                    try:
                        with open(frame.filename, "r") as file:
                            i = frame.lineno - LINES_AROUND - 1
                            j = frame.lineno + LINES_AROUND
                            lines = file.readlines()[i:j]

                    except:
                        logger.write(f"{3*TAB}~~~ unabled to output traceback")

                    else:
                        # Log the traceback if it was possible to read the file.
                        for line_number, line in enumerate(lines, i + 1):
                            marker = "-->" if line_number == frame.lineno else "   "

                            logger.write(
                                f"{2*TAB}"
                                f"{marker} {str(line_number).rjust(padding)}: "
                                f"{line.removesuffix('\n')}"
                            )

                    logger.separate(1)

    logger.separate()

    # If the number of successful tests is equal to the total number of tests, then the
    # exit code of the program should be 0 (everything ok).
    return int(total_count != favorable_count)


if __name__ == "__main__":
    sys.exit(main())
