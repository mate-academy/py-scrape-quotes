from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag
import requests
import csv


BASE_URl = "https://quotes.toscrape.com/page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[
            tag.get_text(strip=True)
            for tag in quote.select(".tag")
        ]
    )


def get_quotes(url: str) -> list[Quote]:
    response = requests.get(url).content
    soup = BeautifulSoup(response, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    page = 1
    all_quotes = []

    while True:
        url = f"{BASE_URl}{page}/"
        quotes = get_quotes(url)

        if not quotes:
            break
        all_quotes.extend(quotes)
        page += 1
    return all_quotes


def write_to_csvfile(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    write_to_csvfile(get_all_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
