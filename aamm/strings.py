import re
from typing import Callable

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def indent(string: str, level: int = 1) -> str:
    return (level * "\t" + string.strip()).replace("\n", "\n" + level * "\t")


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


pattern_dunder = re.compile(r"^__[a-zA-Z0-9_]+__$").match


def is_dunder(string: str) -> bool:
    return bool(pattern_dunder(string))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


pattern_camelcase = re.compile(r"^[a-z]+(?:[A-Z][a-z]+)+$").match


def is_camelcase(string: str) -> bool:
    return bool(pattern_camelcase(string))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


pattern_lowercase = re.compile(r"^[a-z]+$").match


def is_lowercase(string: str) -> bool:
    return bool(pattern_lowercase(string))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


pattern_snakecase = re.compile(r"^[a-z]+(?:_[a-z]+)+$").match


def is_snakecase(string: str) -> bool:
    return bool(pattern_snakecase(string))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


pattern_titlecase = re.compile(r"^(?:[A-Z][a-z]+)+$").match


def is_titlecase(string: str) -> bool:
    return bool(pattern_titlecase(string))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


pattern_uppercase = re.compile(r"^[A-Z]+$").match


def is_uppercase(string: str) -> bool:
    return bool(pattern_uppercase(string))


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def pattern_match(pattern: str) -> Callable:
    match = re.compile(pattern).match

    def is_match(string: str) -> bool:
        return bool(match(string))

    return is_match
