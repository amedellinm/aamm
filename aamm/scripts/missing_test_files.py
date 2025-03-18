import sys

from aamm import file_system as fs
from aamm import meta, metadata
from aamm.logging import Logger
from aamm.testing.core import test_file


def main():
    """Log expected test-file paths that are missing."""

    logger = Logger.from_sys_stream("stdout")

    missing_test_files = {}

    # Look up test files and store the missing paths.
    with fs.cwd_context(metadata.home):
        for file in metadata.header_files:
            if not fs.exists(missing_test_file := test_file(file)):
                module = meta.module_identifier(fs.relative(file))
                missing_test_files[module] = missing_test_file

    # Handle successful case.
    if not missing_test_files:
        return 0

    # Column alignment variables.
    SPACEING = 6 * " "
    l = max(len(i) for i in missing_test_files)
    r = max(len(i) for i in missing_test_files.values())

    # Log results.
    logger.write("MODULE".ljust(l), "MISSING FILE", sep=SPACEING)
    logger.write(l * "-", r * "-", sep=SPACEING)

    for module, missing_test_file in missing_test_files.items():
        logger.write(module.ljust(l), missing_test_file, sep=SPACEING)

    # Return error exit code.
    return 1


if __name__ == "__main__":
    sys.exit(main())
