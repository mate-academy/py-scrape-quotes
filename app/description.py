from dataclasses import dataclass
from datetime import date
from urllib.parse import urljoin


BASE_URL = "https://quotes.toscrape.com/"
EXT_URL_QUOTE = urljoin(BASE_URL, "page/")
EXT_URL_AUTHOR = urljoin(BASE_URL, "author/")
HTML_PARSER = "html.parser"
CLASS_QUOTE = ".quote"
CLASS_AUTHOR = ".author"
AUTHORS_FILE = "authors.csv"
QUOTES_FILE = "correct_quotes.csv"
AUTHOR_FIELD_NAMES = [
    "name",
    "born_date",
    "born_city",
    "born_country",
    "description"
]
QUOTE_FIELD_NAMES = ["text", "author", "tags"]


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass()
class Author:
    name: str
    born_date: date
    born_city: str
    born_country: str
    description: str
