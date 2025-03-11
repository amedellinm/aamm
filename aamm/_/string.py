import re
import textwrap
from collections.abc import Callable


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
        """Return True if `string` matches `pattern`."""
        return bool(compiled_pattern(string))

    return is_match


def indent(
    string: str, level: int = 1, indent: str = "    ", first_indent: str = "    "
) -> str:
    """Indent a string on each series of newlines."""
    first_indent *= level
    indent *= level

    def repl(match: re.Match) -> str:
        start, end = match.span()
        return (end - start) * "\n" + indent

    return re.subn(r"\n+", repl, first_indent + string)[0]


def line_formatter(string: str, formatter: Callable[[str, int], str]) -> str:
    line_index = -1

    def repl(match: re.Match) -> str:
        nonlocal line_index
        line_index += 1
        return formatter(match.group(), line_index)

    return re.subn(r".+(\n|$)", repl, string)[0]


is_dunder = create_matcher(r"^__[a-zA-Z0-9_]+__$")


is_camelcase = create_matcher(r"^[a-z]+(?:[A-Z][a-z]+)+$")


is_lowercase = str.islower


is_snakecase = create_matcher(r"^[a-z]+(?:_[a-z]+)+$")


is_titlecase = str.istitle


is_uppercase = str.isupper


def is_utf8_valid(string: str) -> bool:
    """Validate `string` is utf-8 encodable."""
    try:
        string.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


def right_replace(string: str, old: str, new: str, count: int = 1) -> str:
    """Same as `str.replace` but starting from the right of the string."""
    return string[::-1].replace(old[::-1], new[::-1], count)[::-1]


def wrap(
    string: str,
    width: int,
    as_lines: bool = False,
) -> str | list[str]:
    """Break a single line of text into lines of at most `width` characters."""
    kwargs = {"text": string, "width": width, "break_on_hyphens": False, "tabsize": 4}
    return textwrap.wrap(**kwargs) if as_lines else textwrap.fill(**kwargs)
