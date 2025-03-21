import os
import tempfile
from collections.abc import Iterator

from aamm import file_system as fs
from aamm import metadata, testing
from aamm.testing import asserts


class TestFileSystem(testing.TestSuite):
    @testing.subjects(fs.cd, fs.cwd)
    def test_cd_and_cwd(self):
        cwd = fs.cwd()
        path = fs.directory(cwd)

        fs.cd("..")
        asserts.equal(path, fs.cwd())

        fs.cd(cwd)

    @testing.subjects(fs.current_directory)
    def test_current_directory(self):
        asserts.equal(fs.directory(__file__), fs.current_directory())

    @testing.subjects(fs.current_file)
    def test_current_file(self):
        asserts.equal(__file__, fs.current_file())

    @testing.subjects(fs.cwd_context)
    def test_cwd_context(self):
        cwd = fs.cwd()

        asserts.equal(cwd, fs.cwd())
        with fs.cwd_context(fs.current_directory()):
            asserts.not_equal(cwd, fs.cwd())
        asserts.equal(cwd, fs.cwd())

    @testing.subjects(fs.directories)
    def test_directories(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            directories = []

            for char in "abc":
                directory = fs.join(tmp_dir, char)
                directories.append(directory)
                os.makedirs(directory)

            asserts.equal(directories, sorted(fs.directories(tmp_dir)))
            asserts.equal(
                sorted("abc"), sorted(fs.directories(tmp_dir, leafs_only=True))
            )

    @testing.subjects(fs.directory)
    def test_directory(self):
        directory = "directory"
        path = fs.join(directory, "file.txt")
        asserts.equal(directory, fs.directory(path))

    @testing.subjects(fs.exists)
    def test_exists(self):
        assert fs.exists(__file__)

        with tempfile.TemporaryDirectory() as tmp_dir:
            pass

        assert not fs.exists(tmp_dir)

    @testing.subjects(fs.extension)
    def test_extension(self):
        path = "path/file.txt"
        asserts.equal("txt", fs.extension(path))

        path = "path/file"
        asserts.equal("", fs.extension(path))

        path = "path/.txt"
        asserts.equal("", fs.extension(path))

        path = "path/file.tar.gz"
        asserts.equal("gz", fs.extension(path))

    @testing.subjects(fs.files)
    def test_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            files = []

            for char in "abc":
                file = fs.join(tmp_dir, char + ".txt")
                files.append(file)
                open(file, "w").close()

            asserts.equal(files, sorted(fs.files(tmp_dir)))
            asserts.equal(
                ["a.txt", "b.txt", "c.txt"],
                sorted(fs.files(tmp_dir, leafs_only=True)),
            )

    @testing.subjects(fs.glob)
    def test_glob(self):
        assert isinstance(fs.glob(), Iterator)

    @testing.subjects(fs.has_extension)
    def test_has_extension(self):
        path = "path.txt"
        assert fs.has_extension(path)
        assert not fs.has_extension(path, "py")

        path = "path"
        assert not fs.has_extension(path, "txt")
        assert not fs.has_extension(path)

    @testing.subjects(fs.head, fs.tail)
    def test_head_and_tail(self):
        segments = tuple("12345")
        path = fs.join(*segments)

        for i in range(-5, 6):
            asserts.equal(fs.join(*segments[:+i]), fs.head(path, i))
            asserts.equal(fs.join(*segments[-i:]), fs.tail(path, i))

    @testing.subjects(fs.here)
    def test_here(self):
        asserts.equal(fs.join(fs.current_directory(), "file.txt"), fs.here("file.txt"))

    @testing.subjects(fs.is_directory, fs.is_file, fs.is_symlink)
    def test_is_path_type(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            assert fs.is_directory(tmp_dir)
            tmp_file = fs.join(tmp_dir, "file.txt")
            open(tmp_file, "w").close()
            assert fs.is_file(tmp_file)

    @testing.subjects(fs.join, fs.SEP)
    def test_join(self):
        asserts.equal("path" + fs.SEP + "file.txt", fs.join("path", "file.txt"))

    @testing.subjects(fs.leaf)
    def test_leaf(self):
        path = fs.join("path", "file.txt")
        asserts.equal("file.txt", fs.leaf(path))

    @testing.subjects(fs.name)
    def test_name(self):
        path = fs.join("path", "file.txt")
        asserts.equal("file", fs.name(path))

    @testing.subjects(fs.normalize)
    def test_normalize(self):
        a = fs.join("path", "file.txt")
        b = f"path{fs.SEP}{fs.SEP}file.txt{fs.SEP}"

        asserts.equal(a, fs.normalize(b))

    @testing.subjects(fs.relative)
    def test_relative(self):
        expected = __file__.removeprefix(metadata.home + fs.SEP)
        obtained = fs.relative(__file__, metadata.home)

        asserts.equal(expected, obtained)

    @testing.subjects(fs.remove_extension)
    def test_remove_extension(self):
        a = fs.join("path", "file")
        b = fs.join("path", "file.txt")
        asserts.equal(a, fs.remove_extension(a))
        asserts.equal(a, fs.remove_extension(b))

    @testing.subjects(fs.resolve)
    def test_resolve(self):
        """`fs.resolve` is an alias for `pathlib.Path.resolve`."""

    @testing.subjects(fs.segment)
    def test_segment(self):
        segments = ["path", "file.txt"]
        path = fs.join(*segments)
        asserts.equal(segments[0], fs.segment(path, 0))
        asserts.equal(segments[1], fs.segment(path, 1))

    @testing.subjects(fs.up)
    def test_up(self):
        path = fs.join("path", "file.txt")
        asserts.equal("path", fs.up(path))
        asserts.equal("", fs.up(path, 2))

        path = fs.join("", "path", "file.txt")
        asserts.equal(fs.SEP, fs.up(path, 2))
        asserts.equal(fs.SEP, fs.up(path, 3))
        asserts.equal(fs.SEP, fs.up(path, 4))

    @testing.subjects(fs.with_extension)
    def test_with_extension(self):
        path = fs.join("path", "file.txt")
        expected = fs.join("path", "file.test")
        asserts.equal(expected, fs.with_extension(path, "test"))

    @testing.subjects(fs.with_leaf)
    def test_with_leaf(self):
        path = fs.join("path", "file.txt")
        expected = fs.join("path", "test")
        asserts.equal(expected, fs.with_leaf(path, "test"))

    @testing.subjects(fs.with_name)
    def test_with_name(self):
        path = fs.join("path", "file.txt")
        expected = fs.join("path", "test.txt")
        asserts.equal(expected, fs.with_name(path, "test"))
