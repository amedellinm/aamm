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


def current_filename(ext: str = ...) -> str:
    filename = os.path.basename(inspect.stack()[-1].filename)
    if ext is ...:
        return filename
    name = os.path.splitext(filename)[0]
    if isinstance(ext, str):
        return name + "." + ext
    return name


def current_filepath() -> str:
    return inspect.stack()[-1].filename


def current_foldername() -> str:
    return os.path.basename(os.path.dirname(inspect.stack()[-1].filename))


def current_folderpath() -> str:
    return os.path.dirname(inspect.stack()[-1].filename)


def dir_up(path: str | Path = None, n: int = 1) -> str:
    """Returns `n` directories up the given path."""
    if path is None:
        path = current_folderpath()
    elif os.path.isfile(path):
        path = os.path.dirname(path)
    for _ in range(n):
        path = os.path.dirname(path)
    return path


def here(file_name: str = "") -> str:
    """Constructs the path of a file in the current directory."""
    return os.path.join(current_folderpath(), file_name)


def listfiles(path: str | Path = None) -> list[str]:
    """List all files in `path`."""
    if path is None:
        path = current_folderpath()
    try:
        root, _, files = next(os.walk(path))
    except StopIteration:
        return []
    return [os.path.join(root, file) for file in files]


def listfolders(path: str | Path = None) -> list[str]:
    """List all folders in `path`."""
    if path is None:
        path = current_folderpath()
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
        root = current_folderpath()
    elif root is ...:
        root = os.getcwd()

    if isinstance(condition, str):
        pattern = re.compile(condition).match

        def condition(path: str | Path) -> bool:
            return bool(pattern(os.path.basename(path)))

    queue = [root]
    while queue:
        node = queue.pop()
        if condition(node) ^ use_complement:
            queue.extend(reversed(listfolders(node)))
            yield node
