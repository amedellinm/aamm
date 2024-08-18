import os

import aamm.file_system as fs
from aamm import testing
from aamm.std import import_path


def main():
    for test_folder in fs.search():
        # Filter out all folders not called "__tests".
        if not test_folder.endswith("__tests"):
            continue

        # Every subpackage has a "__tests" folder with test files matching the
        # available modules of the subpackage. By going one directory up and then
        # listing the files, we get the expected names of those test files.
        folder = fs.dir_up(test_folder)
        file_names = frozenset(fs.files(folder, names_only=True))

        for test_file in fs.files(test_folder):
            # Make sure "test_file" corresponds to one of the modules.
            path_base = os.path.basename(test_file)
            if path_base not in file_names:
                continue

            import_path(test_file)

    testing.main()


if __name__ == "__main__":
    main()
