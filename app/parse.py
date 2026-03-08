import csv
import requests
from urllib.parse import urljoin
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]

"""parsing single quote"""


def parse_quote(quote: Tag) -> Quote:
    text = quote.select_one(".text").text.strip("“”")
    author = quote.select_one(".author").text
    tags = [tag.text for tag in quote.select(".tag")]
    return Quote(text=text, author=author, tags=tags)


"""return all quotes on first page"""


def get_quotes(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select(".quote")
    return [parse_quote(quote) for quote in quotes]


"""function for  next page navigation"""


def get_next_page_path(page_soup: BeautifulSoup) -> str | None:
    next_button = page_soup.select_one("li.next a")

    return next_button["href"] if next_button else None


def write_quotes_to_file(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="cp1252", errors="ignore", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        for quote in quotes:
            writer.writerow(astuple(quote))


def get_all_quotes() -> [Quote]:
    current_path = "/"
    all_quotes = []
    while current_path:
        print(f"Parsing: {current_path}")
        response = requests.get(urljoin(BASE_URL, current_path))
        soup = BeautifulSoup(response.content, "html.parser")
        quotes_on_page = get_quotes(soup)
        all_quotes.extend(quotes_on_page)
        current_path = get_next_page_path(soup)
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_file(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
