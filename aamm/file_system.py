import filecmp
import inspect
import os
import re
from pathlib import Path
from typing import Callable, Generator

from aamm.std import depth_first


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


def current_filename(ext: str | None = ..., stack_index: int = 1) -> str:
    filename = os.path.basename(inspect.stack()[stack_index].filename)
    if ext is ...:
        return filename
    name = os.path.splitext(filename)[0]
    if isinstance(ext, str):
        return name + "." + ext
    return name


def current_filepath(stack_index: int = 1) -> str:
    return inspect.stack()[stack_index].filename


def current_foldername(stack_index: int = 1) -> str:
    return os.path.basename(os.path.dirname(inspect.stack()[stack_index].filename))


def current_folderpath(stack_index: int = 1) -> str:
    return os.path.dirname(inspect.stack()[stack_index].filename)


def dir_up(path: str | Path = None, n: int = 1) -> str:
    """Returns `n` directories up the given path."""
    if path is None:
        path = current_folderpath(2)
    elif os.path.isfile(path):
        path = os.path.dirname(path)
    for _ in range(n):
        path = os.path.dirname(path)
    return path


def has_extension(path: str, extension: str = None) -> bool:
    """If given, `extension` must have a leading dot e.g. `".py"`."""
    ext = os.path.splitext(path)[1]
    return bool(ext) if extension is None else extension == ext


def here(file_name: str = "") -> str:
    """Constructs the path of a file in the current directory."""
    return os.path.join(current_folderpath(2), file_name)


def listfiles(path: str | Path = None) -> list[str]:
    """List all files in `path`."""
    if path is None:
        path = current_folderpath(2)
    try:
        root, _, files = next(os.walk(path))
    except StopIteration:
        return []
    return [os.path.join(root, file) for file in files]


def listfolders(path: str | Path = None) -> list[str]:
    """List all folders in `path`."""
    if path is None:
        path = current_folderpath(2)
    try:
        root, folders, _ = next(os.walk(path))
    except StopIteration:
        return []
    return [os.path.join(root, folder) for folder in folders]


def search(
    root: str = None,
    condition: str | Callable = ".",
    use_complement: bool = False,
) -> Generator:
    """From `root`, depth-first traverses folders according to `condition`."""
    if root is None:
        root = current_folderpath(2)
    elif root is ...:
        root = os.getcwd()

    if isinstance(condition, str):
        pattern = re.compile(condition).match

        def condition(path: str | Path) -> bool:
            return bool(pattern(os.path.basename(path)))

    queue = [root]
    while queue:
        if condition(node := queue.pop()) ^ use_complement:
            queue.extend(reversed(listfolders(node)))
            yield node
