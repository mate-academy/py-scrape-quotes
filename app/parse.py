import csv
from dataclasses import dataclass, fields

import requests
from bs4 import Tag, BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [quote.name for quote in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_page_quotes(url: str) -> [Quote]:
    text = requests.get(url).content
    soup = BeautifulSoup(text, "html.parser")
    quote_tags = soup.select(".quote")

    parsed = [parse_single_quote(q) for q in quote_tags]

    next_page = soup.select_one(".next")
    if next_page:
        parsed.extend(get_page_quotes(BASE_URL + next_page.find("a")["href"]))

    return parsed


def write_quotes_to_csv(quotes: [Quote], name_of_file: str) -> None:
    with open(name_of_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)

        for quote in quotes:
            row = [quote.text, quote.author, repr(quote.tags)]
            writer.writerow(row)


def main(output_csv_path: str) -> None:
    quotes = get_page_quotes(BASE_URL)
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
