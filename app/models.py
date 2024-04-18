from dataclasses import dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
