import csv
from dataclasses import dataclass, astuple, fields
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quote(soup: Tag) -> Quote:
    text = soup.select_one(".text").text
    author = soup.select_one(".author").text
    tags = [tag.text for tag in soup.select(".tag")]
    return Quote(
        text=text,
        author=author,
        tags=tags
    )


def get_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [get_single_quote(quote) for quote in quotes]


def get_all_pages() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = get_page_quotes(soup)

    next_ = soup.select_one(".next")

    while next_:
        next_page_part_url = next_.select_one("a")["href"]
        next_page_url = urljoin(BASE_URL, next_page_part_url)

        page = requests.get(next_page_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(get_page_quotes(soup))

        next_ = soup.select_one(".next")

    return quotes


QUOTE_FIELD = [field.name for field in fields(Quote)]


def main(output_csv_path: str) -> None:
    quotes = get_all_pages()
    with open(output_csv_path, "w+", newline="", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELD)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
