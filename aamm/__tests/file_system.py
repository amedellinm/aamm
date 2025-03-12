import os
import tempfile
from collections.abc import Iterator

from aamm import file_system as fs
from aamm.testing import TestSuite, asserts


class TestFileSystem(TestSuite):
    def test_cd_and_cwd(self):
        cwd = fs.cwd()
        path = fs.directory(cwd)

        fs.cd("..")
        asserts.equal(path, fs.cwd())

        fs.cd(cwd)

    def test_current_directory(self):
        asserts.equal(fs.directory(__file__), fs.current_directory())

    def test_current_file(self):
        asserts.equal(__file__, fs.current_file())

    def test_cwd_context(self):
        cwd = fs.cwd()

        asserts.equal(cwd, fs.cwd())
        with fs.cwd_context(fs.current_directory()):
            asserts.not_equal(cwd, fs.cwd())
        asserts.equal(cwd, fs.cwd())

    def test_directories(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            directories = []

            for char in "abc":
                directory = fs.join(tmp_dir, char)
                directories.append(directory)
                os.makedirs(directory)

            asserts.equal(directories, list(fs.directories(tmp_dir)))
            asserts.equal(list("abc"), list(fs.directories(tmp_dir, leafs_only=True)))

    def test_directory(self):
        directory = "directory"
        path = fs.join(directory, "file.txt")
        asserts.equal(directory, fs.directory(path))

    def test_exists(self):
        assert fs.exists(__file__)

        with tempfile.TemporaryDirectory() as tmp_dir:
            pass

        assert not fs.exists(tmp_dir)

    def test_extension(self):
        path = "path/file.txt"
        asserts.equal("txt", fs.extension(path))

        path = "path/file"
        asserts.equal("", fs.extension(path))

        path = "path/.txt"
        asserts.equal("", fs.extension(path))

        path = "path/file.tar.gz"
        asserts.equal("gz", fs.extension(path))

    def test_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            files = []

            for char in "abc":
                file = fs.join(tmp_dir, char + ".txt")
                files.append(file)
                open(file, "w").close()

            asserts.equal(files, list(fs.files(tmp_dir)))
            asserts.equal(
                ["a.txt", "b.txt", "c.txt"],
                list(fs.files(tmp_dir, leafs_only=True)),
            )

    def test_glob(self):
        assert isinstance(fs.glob(), Iterator)

    def test_has_extension(self):
        path = "path.txt"
        assert fs.has_extension(path)
        assert not fs.has_extension(path, "py")

        path = "path"
        assert not fs.has_extension(path, "txt")
        assert not fs.has_extension(path)

    def test_head_and_tail(self):
        segments = tuple("12345")
        path = fs.join(*segments)

        for i in range(-5, 6):
            asserts.equal(fs.join(*segments[:+i]), fs.head(path, i))
            asserts.equal(fs.join(*segments[-i:]), fs.tail(path, i))

    def test_here(self):
        asserts.equal(fs.join(fs.current_directory(), "file.txt"), fs.here("file.txt"))

    def test_segment(self):
        segments = ["path", "file.txt"]
        path = fs.join(*segments)
        asserts.equal(segments[0], fs.segment(path, 0))
        asserts.equal(segments[1], fs.segment(path, 1))

    def test_is_path_type(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            assert fs.is_directory(tmp_dir)
            tmp_file = fs.join(tmp_dir, "file.txt")
            open(tmp_file, "w").close()
            assert fs.is_file(tmp_file)

    def test_join(self):
        asserts.equal("path" + fs.SEP + "file.txt", fs.join("path", "file.txt"))

    def test_leaf(self):
        path = fs.join("path", "file.txt")
        asserts.equal("file.txt", fs.leaf(path))

    def test_name(self):
        path = fs.join("path", "file.txt")
        asserts.equal("file", fs.name(path))

    def test_normalize(self):
        a = fs.join("path", "file.txt")
        b = f"path{fs.SEP}{fs.SEP}file.txt{fs.SEP}"

        asserts.equal(a, fs.normalize(b))

    def test_relative(self):
        expected = fs.resolve(__file__).removeprefix(fs.resolve(fs.cwd()) + fs.SEP)
        obtained = fs.relative(__file__)

        asserts.equal(expected, obtained)

    def test_remove_extension(self):
        a = fs.join("path", "file")
        b = fs.join("path", "file.txt")
        asserts.equal(a, fs.remove_extension(b))
