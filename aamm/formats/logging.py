from datetime import datetime as DateTime

from aamm.formats import indent


def tag_header_body(tag: str = ..., header: str = "", body: str = "") -> str:
    if tag is ...:
        tag = DateTime.now()

    msg = f"[{tag.upper()}]: {header}"
    if body:
        msg += f"\n{indent(body)}"

    return msg
