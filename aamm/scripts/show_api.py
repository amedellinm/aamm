import sys

import aamm
from aamm import file_system as fs
from aamm import meta
from aamm.logging import Logger
from aamm.logging.formats import contents_table_row, exception_message


def main():
    logger = Logger.from_sys_stream("stdout")

    cwd = fs.cwd()
    fs.cd(root := fs.directory(aamm.__path__[0]))

    for path in sorted(fs.search("**/*.py", root)):
        segments = path.split(fs.SEP)

        if segments[0] != "aamm":
            continue
        if segments[1] == "scripts":
            continue
        if "_" in segments:
            continue
        if "__tests" in segments:
            continue

        logger.write(
            fs.remove_extension(path).replace(fs.SEP, ".").removesuffix(".__init__")
        )

        try:
            module = meta.import_path(path)
        except Exception as e:
            logger.write(f"    {exception_message(e)}")
        else:
            for key, value in vars(module).items():
                if key.startswith("_"):
                    continue

                logger.write(
                    "   ", contents_table_row(key, type(value).__qualname__, 70)
                )

        logger.separate(1)

    # Resume CWD.
    fs.cd(cwd)


if __name__ == "__main__":
    sys.exit(main())
