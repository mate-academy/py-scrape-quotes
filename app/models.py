from datetime import date
from dataclasses import dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    name: str
    born: date
    location: str
