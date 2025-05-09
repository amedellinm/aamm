import ast

from aamm import file_system as fs
from aamm import metadata
from aamm.logging import Logger


def main():
    """Check from-import statements are the only source code in the header files."""

    logger = Logger.from_string_io()
    exit_code = 0

    for header_file in metadata.header_files:
        with open(header_file) as file:
            src = file.read()

        if bad_nodes := [
            f"  - {type(node).__qualname__} {node.lineno}:{node.end_lineno}"
            for node in next(ast.walk(ast.parse(src))).body
            if not isinstance(node, ast.ImportFrom)
        ]:
            logger.write(fs.relative(header_file, metadata.home))
            logger.write(*bad_nodes, sep="\n", end="\n\n")

            exit_code = 1

    print(logger.stream.getvalue().strip() or "OK")

    return exit_code


if __name__ == "__main__":
    import sys

    sys.exit(main())
