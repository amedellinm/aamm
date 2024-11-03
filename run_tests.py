import os

import aamm.file_system as fs
from aamm import testing
from aamm.meta import import_path


def main():
    TEST_DIRECTORY_NAME = "__tests"
    TEST_FILE_PREFIX = "test_"

    def condition(directory: str) -> bool:
        return os.path.basename(directory) != TEST_DIRECTORY_NAME

    # Adding `condition` to `fs.search` makes sure test directories are not expanded,
    # meaning, directories within test directories will never show up in the search.
    for test_directory in fs.search(fs.current_directory(), condition):

        # Filter out all directories not called `TEST_DIRECTORY_NAME`.
        if condition(test_directory):
            continue

        # Every subpackage has a `TEST_DIRECTORY_NAME` directory with test files
        # matching the available modules of the subpackage. By going one directory up
        # and then listing the files, we get the expected names of those test files.
        filenames = frozenset(fs.files(fs.up(test_directory), names_only=True))

        for test_file in fs.files(test_directory):
            basename = os.path.basename(test_file)
            filename = basename.removeprefix(TEST_FILE_PREFIX)

            # Make sure `test_file` is a test file and it corresponds to one of the
            # modules in the current subpackage.
            if basename.startswith(TEST_FILE_PREFIX) and filename in filenames:
                import_path(test_file)

    testing.main()


if __name__ == "__main__":
    main()
