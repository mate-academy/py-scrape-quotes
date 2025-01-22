from dataclasses import dataclass, fields, astuple
import requests
import bs4
import csv
from typing import List

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


def get_quotes() -> List[Quote]:
    quotes = []
    next_page = BASE_URL
    while next_page:
        response = requests.get(next_page)
        soup = bs4.BeautifulSoup(response.text, "html.parser")
        for quote_tag in soup.select(".quote"):
            quotes.append(parse_single_quote(quote_tag))

        next_button = soup.select_one(".next > a")
        if next_button:
            next_page = BASE_URL + next_button["href"]
        else:
            next_page = None

    return quotes


def quotes_to_csv(quotes: List[Quote], file_name: str) -> None:
    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes_to_csv(get_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
