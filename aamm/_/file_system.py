import glob
import inspect
import os
import pathlib
from collections.abc import Iterator

SEP = os.path.sep


def current_directory(stack_index: int = 0) -> str:
    """Get the directory path of the source file of the caller."""
    return directory(current_file(stack_index=stack_index + 1))


def current_file(stack_index: int = 0) -> str:
    """Get the path of the source file of the caller."""
    return inspect.stack()[stack_index + 1].frame.f_globals["__file__"]


def cwd() -> str:
    """Return the current working directory."""
    return os.getcwd()


def directories(root: str, leafs_only: bool = False) -> list[str]:
    """List all directories in `root`."""
    root, paths, _ = next(os.walk(root), (None, None, []))
    if leafs_only:
        return paths
    return [os.path.join(root, subpath) for subpath in paths]


def directory(path: str, base_only: bool = False) -> str:
    """Return the directory component of `path`."""
    directory_path = os.path.dirname(path)
    return leaf(directory_path) if base_only else directory_path


def exists(path: str) -> bool:
    """Check path exists."""
    return os.path.exists(path)


def extension(path: str) -> str:
    """Return the extension of `path`."""
    i = path.rfind(".")
    return path[i + 1 :] if i > 0 else ""


_extension = extension


def files(root: str, leafs_only: bool = False) -> list[str]:
    """List all files in `root`."""
    root, _, paths = next(os.walk(root), (None, None, []))
    if leafs_only:
        return paths
    return [os.path.join(root, subpath) for subpath in paths]


def has_extension(path: str, extension: str = None) -> bool:
    """Check `path` has extension `extension`."""
    expected = extension.removeprefix(".")
    obtained = _extension(path)
    return bool(obtained) if extension is None else expected == obtained


def head(path: str, n: int = 1) -> str:
    """Return the first `n` segments of a path."""
    return SEP.join(path.split(SEP)[:n])


def here(*path_segments: tuple[str], stack_index: int = 0) -> str:
    """Construct a path in the current directory."""
    return os.path.join(
        current_directory(stack_index=stack_index + 1), SEP.join(path_segments)
    )


def is_directory(path: str) -> bool:
    """Test whether `path` is a directory."""
    return os.path.isdir(path)


def is_file(path: str) -> bool:
    """Test whether `path` is a file."""
    return os.path.isfile(path)


def is_symlink(path: str) -> bool:
    """Test whether `path` is a symlink."""
    return os.path.islink(path)


def join(*path_segments: tuple[str]) -> str:
    """Join `path_segments` using the OS path separator."""
    return SEP.join(path_segments)


def leaf(path: str) -> str:
    """Return the last component of `path`."""
    return os.path.basename(path)


def name(path: str) -> str:
    """Return the leaf of `path` without the extension."""
    s = leaf(path)
    i = s.rfind(".")
    return s if i == -1 else s[:i] or s[i:]


_name = name


def normalize(path: str) -> str:
    """Remove redundant and trailing `SEP`s."""
    return SEP.join(part for part in path.split(SEP) if part).strip(SEP)


def relative(path: str) -> str:
    """Return `path` relative to the cwd."""
    return os.path.relpath(path)


def remove_extension(path: str) -> str:
    """Return an extensionless version of `path`."""
    return path.removesuffix("." + _extension(path))


def resolve(path: str) -> str:
    """Return the resolve version of `path`."""
    return str(pathlib.Path(path).resolve())


def search(
    root: str = None,
    pattern: str = "*",
    absolute: bool = True,
    recursive: bool = True,
    include_hidden: bool = True,
) -> Iterator[str]:
    """Yield paths matching `pattern`."""
    if root is None:
        root = cwd()

    paths = glob.iglob(
        pattern, root_dir=root, recursive=recursive, include_hidden=include_hidden
    )

    if absolute:
        return map(lambda path: resolve(join(root, path)), paths)
    return paths


def segment(path: str, index: int) -> str:
    if index == -1:
        return leaf(path)
    return path.split(SEP)[index]


def tail(path: str, n: int = 1) -> str:
    """Return the last `n` segments of a path."""
    return SEP.join(path.split(SEP)[-n:])


def to_directory(path: str) -> str:
    """idempotent if `path` is a directory, gets the directory otherwise."""
    return path if is_directory(path) else directory(path)


def up(path: str, n: int = 1) -> str:
    """Move `n` segments up the given path."""
    for _ in range(n):
        path = directory(path)
    return path


def with_extension(path: str, extension: str) -> str:
    """Substitute the extension of `path`."""
    return remove_extension(path) + "." + extension


def with_leaf(path: str, leaf: str) -> str:
    """Substitute the leaf of `path`."""
    return join(directory(path), leaf)


def with_name(path: str, name: str) -> str:
    """Substitute the name of `path`."""
    old_name = _name(path)
    i = path.rfind(old_name)
    return path[:i] + name + path[i + len(old_name) :]
