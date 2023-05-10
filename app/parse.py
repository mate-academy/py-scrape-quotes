import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com/page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    tags = [tag.text for tag in quote_soup.select(".tag")]
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags
    )


def get_page_info(url: str) -> dict:
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")
    next_page_link = soup.select_one(".next a")
    quotes = soup.select(".quote")
    result = {
        "quotes": [parse_single_quote(quote) for quote in quotes],
        "next": next_page_link["href"] if next_page_link else None
    }
    return result


def get_all_quotes() -> list[Quote]:
    quotes = []
    page = 1
    while True:
        page_info = get_page_info(URL + f"{page}/")
        quotes.extend(page_info["quotes"])
        if not page_info["next"]:
            break
        page += 1
    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes=quotes, output_csv_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
