import argparse
import sys

from aamm import file_system as fs
from aamm import testing
from aamm.iterable import group_by, split_iter
from aamm.logging import Logger


def main(root: str) -> int:
    logger = Logger.from_sys_stream("stdout")

    def format_line(line: str) -> str:
        if line.startswith(">"):
            logger.write(1 * "    " + line)
            return
        logger.write(2 * "    " + line)

    root = fs.resolve(root)
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
        module = fs.remove_extension(module_path).replace(fs.SEP, ".")
        score = f"{len(successful_tests):,}|{len(tests):,}"
        filler = 84 - len(module) - len(score)

        logger.write(f"{module}  {filler*'.'}  {score}")

        # Group failed tests based on suite name.
        for suite, tests in group_by((t.suite_name, t) for t in failed_tests).items():
            logger.write(f"    {suite}")

            for t in tests:
                format_line(f"{t.test_name} -- {t.error_message}")

                stack = t.traceback_stack

                padding = len(str(max(f.lineno for f in stack) + 2))

                for frame in stack:
                    with open(frame.filename, "r") as file:
                        i = frame.lineno - 3
                        j = frame.lineno + 2
                        lines = file.readlines()[i:j]

                    filename = fs.resolve(frame.filename).removeprefix(root + fs.SEP)
                    format_line(f"    {filename}  ({frame.name})")

                    for no, line in enumerate(lines, i + 1):
                        marker = "-->" if no == frame.lineno else "   "
                        format_line(
                            f"{marker}{no:> {padding}}: {line.removesuffix('\n')}"
                        )

                    logger.separate(1)

    logger.separate()

    # If the number of successful tests is equal to the total number of tests, then the
    # exit code of the program should be 0 (everything ok).
    return int(total_count != favorable_count)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=fs.up(fs.current_directory()))
    exit_code = main(ap.parse_args().root)

    sys.exit(exit_code)
