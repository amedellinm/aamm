import re
from typing import Callable

from aamm import meta

TAB = 4 * " "


def indent(string: str, level: int = 1, indent_str=TAB) -> str:
    """Indent a string on each series of newlines."""
    indent_str *= level

    def repl(match: re.Match) -> str:
        start, end = match.span()
        return (end - start) * "\n" + indent_str

    return re.subn(r"\n+", repl, indent_str + string)[0]


def is_utf8_valid(string: str) -> bool:
    """Validate `string` is utf-8 encodable."""
    try:
        string.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


class pattern_match(metaclass=meta.NameSpace):
    @staticmethod
    def create_matcher(pattern: str) -> Callable[[str], bool]:
        """
        DESCRIPTION
        -----------
        Create a callable that takes a string and returns a `bool` indicating whether
        the string is matched by `pattern` or not using `re.Pattern.search`.

        PARAMETERS
        ----------
        pattern:
            * A regular expression to compile as `re.Pattern`.

        """
        compiled_pattern = re.compile(pattern).search

        def is_match(string: str) -> bool:
            return bool(compiled_pattern(string))

        return is_match

    dunder = create_matcher(r"^__[a-zA-Z0-9_]+__$")
    camelcase = create_matcher(r"^[a-z]+(?:[A-Z][a-z]+)+$")
    lowercase = create_matcher(r"^[a-z]+$")
    snakecase = create_matcher(r"^[a-z]+(?:_[a-z]+)+$")
    titlecase = create_matcher(r"^(?:[A-Z][a-z]+)+$")
    uppercase = create_matcher(r"^[A-Z]+$")
