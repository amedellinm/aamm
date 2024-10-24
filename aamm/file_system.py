import inspect
import os
from types import EllipsisType
from typing import Callable, Iterator

from aamm import std


def current_directory(name_only: bool = False, stack_index: int = 0) -> str:
    """Get the directory path of the source file of the caller."""
    directory_path = os.path.dirname(current_file(stack_index=stack_index + 1))
    return os.path.basename(directory_path) if name_only else directory_path


def current_file(
    extension: EllipsisType | None | str = ...,
    name_only: bool = False,
    stack_index: int = 0,
) -> str:
    """
    DESCRIPTION
    -----------
    Get the path of the source file of the caller.

    PARAMETERS
    ----------
    extension:
        * If `...` get the path with its original extension.
        * If `None` get the path without the dot and the extension.
        * If `str` get the path substituting its original extension with `extension`.
        * `extension` is not expected to have a leading dot.

    name_only:
        * If `False` get the full path.
        * If `True` get only the basename of the path.

    stack_index:
        * The stack index used by `inspect`. Index `0` is the stack of the caller.

    """

    file = inspect.stack()[stack_index + 1].frame.f_globals["__file__"]

    if name_only:
        file = os.path.basename(file)

    if extension is ...:
        return file

    name = os.path.splitext(file)[0]
    if extension is None:
        return name

    return name + "." + extension


def directories(root: str, names_only: bool = False) -> list[str]:
    """List all directories in `root`."""
    try:
        root, paths, _ = next(os.walk(root))
    except StopIteration:
        return []
    if names_only:
        return paths
    return [os.path.join(root, subpath) for subpath in paths]


def files(root: str, names_only: bool = False) -> list[str]:
    """List all files in `root`."""
    try:
        root, _, paths = next(os.walk(root))
    except StopIteration:
        return []
    if names_only:
        return paths
    return [os.path.join(root, subpath) for subpath in paths]


def has_extension(path: str, extension: str = None) -> bool:
    """Check `path` has extension `extension`."""
    obtained = os.path.splitext(path)[1].removeprefix(".")
    expected = extension.removeprefix(".")
    return bool(obtained) if expected is None else expected == obtained


def here(filename: str, stack_index: int = 0) -> str:
    """Construct the path of a file in the current directory."""
    return os.path.join(current_directory(stack_index=stack_index + 1), filename)


def search(root: str, expand_condition: Callable = lambda _: True) -> Iterator[str]:
    """
    DESCRIPTION
    -----------
    From `root`, breadth-first traverse directories according to `expand_condition`.

    PARAMETERS
    ----------
    expand_condition:
        * A callable that receives a node (directory path) and returns a boolean.
        * If `expand_condition(node) == True` the node's children are queued.
        * Every queued node is yielded, even if `expand_condition(node) == False`.

    """

    return std.breadth_first(
        root, lambda node: directories(node) if expand_condition(node) else ()
    )


def up(path: str, n: int = 1) -> str:
    """Move `n` segments up the given path."""
    for _ in range(n):
        path = os.path.dirname(path)
    return path
