from dataclasses import dataclass


@dataclass
class Author:
    """Author data model."""

    name: str
    born_date: str
    born_location: str
    description: str


@dataclass
class Quote:
    """Quote data model."""

    text: str
    author: str
    tags: list[str]
