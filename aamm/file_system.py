import filecmp
import inspect
import os
from types import EllipsisType
from typing import Callable, Iterator

import aamm.strings.match as match
from aamm.std import breadth_first, depth_first


def are_directories_equal(d1: str, d2: str) -> bool:
    """Check stat-based equality between two dir trees."""
    for cmp in depth_first(
        filecmp.dircmp(d1, d2, ignore=[]), lambda x: x.subdirs.values()
    ):
        try:
            if cmp.diff_files:
                return False
        except FileNotFoundError:
            return False
    return True


def current_file(
    extension: str | EllipsisType | None = ...,
    name_only: bool = False,
    stack_index: int = 0,
) -> str:
    file = inspect.stack()[stack_index + 1].frame.f_globals["__file__"]
    if name_only:
        file = os.path.basename(file)

    if extension is ...:
        return file

    name = os.path.splitext(file)[0]
    if extension is None:
        return name

    return name + "." + extension


def current_directory(name_only: bool = False, stack_index: int = 0) -> str:
    directory_path = os.path.dirname(current_file(stack_index=stack_index + 1))
    return os.path.basename(directory_path) if name_only else directory_path


def dir_up(path: str | None = None, n: int = 1, stack_index: int = 0) -> str:
    """Returns `n` directories up the given path."""
    if path is None:
        path = current_directory(stack_index=stack_index + 1)
    elif os.path.isfile(path):
        path = os.path.dirname(path)
    for _ in range(n):
        path = os.path.dirname(path)
    return path


def files(
    path: str | None = None, names_only: bool = False, stack_index: int = 0
) -> list[str]:
    """List all files in `path`."""
    if path is None:
        path = current_directory(stack_index=stack_index + 1)
    try:
        root, _, subpaths = next(os.walk(path))
    except StopIteration:
        return []
    if names_only:
        return subpaths
    return [os.path.join(root, subpath) for subpath in subpaths]


def file_name(path: str) -> tuple[str, str]:
    return os.path.splitext(os.path.basename(path))


def directories(
    path: str | None = None, names_only: bool = False, stack_index: int = 0
) -> list[str]:
    """List all directories in `path`."""
    if path is None:
        path = current_directory(stack_index=stack_index + 1)
    try:
        root, subpaths, _ = next(os.walk(path))
    except StopIteration:
        return []
    if names_only:
        return subpaths
    return [os.path.join(root, subpath) for subpath in subpaths]


def has_extension(path: str, extension: str = None) -> bool:
    """Check `path` has extension `extension`."""
    ext = os.path.splitext(path)[1].removeprefix(".")
    extension = extension.removeprefix(".")
    return bool(ext) if extension is None else extension == ext


def here(file_name: str = "", stack_index: int = 0) -> str:
    """Constructs the path of a file in the current directory."""
    return os.path.join(current_directory(stack_index=stack_index + 1), file_name)


def search(
    root: str | EllipsisType | None = None,
    condition: str | Callable | None = None,
    use_complement: bool = False,
    use_breadth_first: bool = False,
    stack_index: int = 0,
) -> Iterator[str]:
    """From `root`, depth-first traverses directories according to `condition`."""
    if root is None:
        root = current_directory(stack_index=stack_index + 1)
    elif root is ...:
        root = os.getcwd()

    explore = breadth_first if use_breadth_first else depth_first

    if condition is None:
        return explore(root, expand=directories)

    if isinstance(condition, str):
        condition = match.create_matcher(condition)

    def expand(node):
        if condition(node) ^ use_complement:
            return directories(node)
        return ()

    return explore(root, expand)
