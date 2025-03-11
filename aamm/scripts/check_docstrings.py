import ast

from aamm import file_system as fs
from aamm import metadata
from aamm.logging import Logger
from aamm.logging import formats as fmts


def main():
    logger = Logger.from_sys_stream("stdout")

    file_table = {}

    with fs.cwd_context(metadata.home):
        for path in metadata.source_files:
            try:
                # Attempt to read the source code.
                with open(path) as src:
                    tree = ast.parse(src.read())

            except Exception as e:
                # Store the exception message.
                file_table[path] = fmts.exception_message(e)

            else:
                # Get the name of all callable symbols missing a docstring.
                docless_symbols = [
                    node.name
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                    # The name of the symbol is not private based on _ naming
                    # convention.
                    and node.name[:1].isalpha()
                    # The symbol is missing its docstring.
                    and ast.get_docstring(node) is None
                ]

                # Store them if any.
                if docless_symbols:
                    file_table[path] = docless_symbols

    # Handle successful case.
    if not file_table:
        logger.write("OK")
        return 0

    # Log header.
    logger.write(fmts.underlined_title("DOCSTRING-MISSING SYMBOLS"))

    for file, payload in file_table.items():
        logger.write(file)

        if isinstance(payload, str):
            # Log exception.
            logger.write("  *", payload)
        else:
            # Log symbols.
            for symbol_name in payload:
                logger.write(f"  - {symbol_name}")

        logger.separate(1)

    # Return error exit code.
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
