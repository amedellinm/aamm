from aamm import file_system as fs
from aamm import meta, metadata
from aamm.logging import Logger
from aamm.logging import formats as fmts


def main():
    logger = Logger.from_sys_stream("stdout")

    with fs.cwd_context(metadata.home):
        for path in map(fs.relative, metadata.header_files):
            logger.write(fmts.module_identifier(path))

            try:
                module = meta.import_path(path)
            except Exception as e:
                logger.write("   ", fmts.exception_message(e))
            else:
                for key, value in vars(module).items():
                    if key[:1].isalpha():
                        msg = fmts.contents_table_row(
                            key, type(value).__qualname__, 70
                        )
                        logger.write("   ", msg)

            logger.separate(1)


if __name__ == "__main__":
    import sys

    sys.exit(main())
