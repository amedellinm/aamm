from aamm import file_system as fs
from aamm import meta, metadata
from aamm.logging import Logger
from aamm.logging import formats as fmts


def main():
    """Log the public symbols grouped by module."""

    logger = Logger.from_sys_stream("stdout")

    with fs.cwd_context(metadata.home):
        for path in map(fs.relative, metadata.header_files):
            logger.write(fmts.module_identifier(path))

            try:
                module = meta.import_path(path)
            except Exception as e:
                # Log exception.
                logger.write("   ", fmts.exception_message(e))
            else:
                # Log symbols.
                for key, value in vars(module).items():
                    if key[:1].isalpha():
                        logger.write(
                            "   ",
                            fmts.contents_table_row(key, fmts.qualname(value), 70),
                        )

            logger.separate(1)


if __name__ == "__main__":
    import sys

    sys.exit(main())
