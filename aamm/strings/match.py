import re
from typing import Callable


def create_matcher(pattern: str) -> Callable:
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
