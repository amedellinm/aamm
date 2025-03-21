from aamm import file_system as fs
from aamm import meta, metadata
from aamm.iterable import group_by
from aamm.logging import Logger
from aamm.logging import formats as fmts


def main():
    """Log the public symbols grouped by module."""

    logger = Logger.from_sys_stream("stdout")

    # Group symbols by header file.
    header_file_groups: dict[str, tuple[metadata.SymbolInfo]] = group_by(
        (meta.module_identifier(fs.relative(si.header_file, metadata.home)), si)
        for si in metadata.api_symbols().values()
    )

    for header_file, symbols_info in sorted(header_file_groups.items()):
        logger.write(header_file)
        for si in symbols_info:
            if not si.is_child:
                logger.write(
                    "   ",
                    fmts.contents_table_row(si.name, fmts.qualname(si.value), 70),
                )

        logger.separate(1)


if __name__ == "__main__":
    import sys

    sys.exit(main())
