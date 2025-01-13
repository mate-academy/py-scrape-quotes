import csv
import requests

from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    tags = [tag.text for tag in quote.select(".tag")]

    return Quote(
        text=quote.select_one("span.text").text,
        author=quote.select_one(".author").text,
        tags=tags,
    )


def get_quotes() -> [Quote]:
    quotes = []
    next_page_url = BASE_URL

    while next_page_url:
        response = requests.get(next_page_url)
        soup = BeautifulSoup(response.content, "html.parser")

        for quote_tag in soup.select(".quote"):
            quotes.append(parse_single_quote(quote_tag))

        next_button = soup.select_one(".next > a")
        if next_button:
            next_page_url = BASE_URL + next_button["href"]
        else:
            next_page_url = None

    return quotes

def write_quotes_to_csv(quotes: [Quote], file_name: str) -> None:
    with open(file_name, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
