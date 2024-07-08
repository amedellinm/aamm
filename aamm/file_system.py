import filecmp
import inspect
import os
from pathlib import Path
from typing import Callable, Generator

from aamm.std import breadth_first, depth_first
from aamm.strings import match


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
    extension: str | None = ..., name_only: bool = False, stack_index: int = 1
) -> str:
    file = inspect.stack()[stack_index].filename
    if name_only:
        file = os.path.basename(file)

    if extension is ...:
        return file

    name = os.path.splitext(file)[0]
    if extension is None:
        return name

    return name + "." + extension


def current_folder(name_only: bool = False, stack_index: int = 1) -> str:
    folder_path = os.path.dirname(inspect.stack()[stack_index].filename)
    return os.path.basename(folder_path) if name_only else folder_path


def dir_up(path: str | Path = None, n: int = 1, stack_index: int = 2) -> str:
    """Returns `n` directories up the given path."""
    if path is None:
        path = current_folder(stack_index=stack_index)
    elif os.path.isfile(path):
        path = os.path.dirname(path)
    for _ in range(n):
        path = os.path.dirname(path)
    return path


def files(
    path: str = None, names_only: bool = False, stack_index: int = 2
) -> list[str]:
    """List all files in `path`."""
    if path is None:
        path = current_folder(stack_index=stack_index)
    try:
        root, _, subpaths = next(os.walk(path))
    except StopIteration:
        return []
    if names_only:
        return subpaths
    return [os.path.join(root, subpath) for subpath in subpaths]


def file_name(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def folders(
    path: str = None, names_only: bool = False, stack_index: int = 2
) -> list[str]:
    """List all folders in `path`."""
    if path is None:
        path = current_folder(stack_index=stack_index)
    try:
        root, subpaths, _ = next(os.walk(path))
    except StopIteration:
        return []
    if names_only:
        return subpaths
    return [os.path.join(root, subpath) for subpath in subpaths]


def has_extension(path: str, extension: str = None) -> bool:
    """If given, `extension` must have a leading dot e.g. `".py"`."""
    ext = os.path.splitext(path)[1]
    return bool(ext) if extension is None else extension == ext


def here(file_name: str = "", stack_index: int = 2) -> str:
    """Constructs the path of a file in the current directory."""
    return os.path.join(current_folder(stack_index=stack_index), file_name)


def search(
    root: str = None,
    condition: str | Callable = ".",
    use_complement: bool = False,
    use_breadth_first: bool = False,
    stack_index: int = 2,
) -> Generator:
    """From `root`, depth-first traverses folders according to `condition`."""
    if root is None:
        root = current_folder(stack_index=stack_index)
    elif root is ...:
        root = os.getcwd()

    if isinstance(condition, str):
        condition = match.create_matcher(condition)

    def expand(node):
        if condition(node) ^ use_complement:
            return folders(node)
        return []

    return (breadth_first if use_breadth_first else depth_first)(root, expand)
