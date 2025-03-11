import sys

from aamm import file_system as fs
from aamm import metadata
from aamm.logging import Logger
from aamm.logging import formats as fmts
from aamm.testing.core import test_file


def main():
    logger = Logger.from_sys_stream("stdout")

    missing_test_files = {}

    with fs.cwd_context(metadata.home):
        for file in metadata.header_files:
            if not fs.exists(missing_test_file := test_file(file)):
                module = fmts.module_identifier(fs.relative(file))
                missing_test_files[module] = missing_test_file

    if not missing_test_files:
        return 0

    SPACEING = 6 * " "
    l = max(len(i) for i in missing_test_files)
    r = max(len(i) for i in missing_test_files.values())

    logger.write("MODULE".ljust(l), "MISSING FILE", sep=SPACEING)
    logger.write(l * "-", r * "-", sep=SPACEING)

    for module, missing_test_file in missing_test_files.items():
        logger.write(module.ljust(l), missing_test_file, sep=SPACEING)

    return 1


if __name__ == "__main__":
    sys.exit(main())
