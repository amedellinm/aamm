import re

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
