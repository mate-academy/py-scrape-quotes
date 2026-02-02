from dataclasses import dataclass, fields


URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


@dataclass
class Author:
    name: str
    birth_date: str
    birth_location: str
    biography: str


AUTHOR_FIELDS = [field.name for field in fields(Author)]
