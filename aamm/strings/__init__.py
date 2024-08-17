import re
from typing import Iterable

TAB = 4 * " "


def is_utf8_valid(string: str) -> bool:
    try:
        string.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


def indent(string: str, level: int = 1, indent_str=TAB) -> str:
    indent_str *= level

    def repl(match: re.Match) -> str:
        start, end = match.span()
        return (end - start) * "\n" + indent_str

    return re.subn(r"(\n)+", repl, indent_str + string)[0]


def join_prepend(string: str, iterable: Iterable[str]):
    return string + string.join(iterable)
