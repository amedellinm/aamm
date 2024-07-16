def is_utf8_valid(string: str) -> bool:
    try:
        string.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


def indent(string: str, level: int = 1) -> str:
    return (level * "\t" + string.strip()).replace("\n", "\n" + level * "\t")
