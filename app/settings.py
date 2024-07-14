from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"

page = requests.get(BASE_URL).content
soup = BeautifulSoup(page, "html.parser")
