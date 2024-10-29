from typing import TypedDict, Literal


class MessageData(TypedDict, total=False):
    role: Literal["user", "assistant"]
    content: str
