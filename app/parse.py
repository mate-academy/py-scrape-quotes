import csv
import requests
from urllib.parse import urljoin
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
URLS = [BASE_URL]


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    tags = quote.select_one(".tags")
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in tags.select(".tag")]
    )


def all_pages() -> None:
    text = requests.get(URLS[-1]).content
    soup = BeautifulSoup(text, "html.parser")
    pagination = soup.select_one(".next")

    if pagination:
        next_page_href = pagination.select_one("a")["href"]
        url_next_page = urljoin(BASE_URL, next_page_href)
        URLS.append(url_next_page)

        all_pages()


def parse_single_page(url: "str") -> [Quote]:
    text = requests.get(url).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    result = [parse_single_quote(quote) for quote in quotes]

    return result


def parse_all_pages() -> list:
    results = []
    all_pages()
    for url in URLS:
        results.extend(parse_single_page(url))

    return results


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        quotes = parse_all_pages()
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
