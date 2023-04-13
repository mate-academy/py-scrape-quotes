import csv
from urllib.parse import urljoin
import requests
from dataclasses import astuple, dataclass, fields
from bs4 import BeautifulSoup, Tag


QUOTE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    page = requests.get(QUOTE_URL).content
    quote_soup = BeautifulSoup(page, "html.parser")
    all_quotes = get_single_page_quotes(quote_soup)

    next_page = quote_soup.select_one(".next")

    while next_page:
        next_page_url = urljoin(
            QUOTE_URL,
            next_page.select_one("a")["href"]
        )

        page = requests.get(next_page_url).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

        next_page = soup.select_one(".next")

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w+", newline="", encoding="UTF-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
