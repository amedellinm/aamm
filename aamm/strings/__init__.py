import aamm.strings.match as match


def indent(string: str, level: int = 1) -> str:
    return (level * "\t" + string.strip()).replace("\n", "\n" + level * "\t")
