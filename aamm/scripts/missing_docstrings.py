from aamm import file_system as fs
from aamm import metadata
from aamm.iterable import group_by
from aamm.logging import Logger
from aamm.logging import formats as fmts


def main():
    """
    Log the name of all the callable symbols in the codebase missing a docstring.
    Ignore symbols whose names start with an '_'.

    """

    logger = Logger.from_sys_stream("stdout")

    header_file_groups: dict[str, tuple[metadata.SymbolInfo]] = group_by(
        (fs.relative(si.header_file, metadata.home), si)
        for si in metadata.api_symbols().values()
        if not si.has_docstring and isinstance(si.source_file, str)
    )

    if not header_file_groups:
        logger.write("OK")
        return 0

    logger.separate()

    logger.write(
        fmts.underlined_title(
            "Missing DOCSTRINGS for the following public symbols "
            f"({len(header_file_groups):,})"
        )
    )

    for header_file, symbols_info in header_file_groups.items():
        # Log symbol info.
        logger.write(f"{header_file} ({len(symbols_info)})")
        for symbol_info in symbols_info:
            logger.write("  -", symbol_info.name)

        logger.separate(1)

    logger.separate(1, forced=True)

    # Return error exit code.
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
