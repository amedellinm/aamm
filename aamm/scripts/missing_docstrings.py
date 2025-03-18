from aamm import metadata
from aamm.logging import Logger
from aamm.logging import formats as fmts


def main():
    """
    Log the name of all the callable symbols in the codebase missing a docstring.
    Ignore symbols whose names start with an '_'.

    """

    logger = Logger.from_sys_stream("stdout")

    symbols = tuple(
        (symbol, symbol_info)
        for symbol, symbol_info in metadata.api_symbols().items()
        if not (symbol_info.has_docstring or symbol_info.source_file is ...)
    )

    logger.write(
        fmts.underlined_title(
            "Missing DOCSTRINGS for the following public symbols "
            f"({len(symbols):,})"
        )
    )

    for symbol, symbol_info in symbols:
        logger.write(f"    name: {symbol.name}")
        logger.write(f"    type: {type(symbol.value).__qualname__}")
        logger.write(f"    source_file: {symbol_info.source_file}")
        logger.write(f"    header_files: {symbol_info.header_files}")
        logger.write(f"    has_docstring: {symbol_info.has_docstring}")
        logger.write(f"    is_child: {symbol_info.is_child}")
        logger.separate(1, flush=False)

    # Log blank space.
    logger.undo(ignore_empty=True)
    logger.separate(forced=True)

    # Return error exit code.
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
