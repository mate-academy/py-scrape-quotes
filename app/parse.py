import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


URL = "https://quotes.toscrape.com/"
PAGE = "page/{page}/"


def parse_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_quotes() -> list[Quote]:
    next_page = 1
    quotes = []
    while next_page:
        res = requests.get(URL + PAGE.format(page=next_page)).content
        soup = BeautifulSoup(res, "html.parser")
        quotes.extend(soup.select(".quote"))
        paging = soup.select_one(".pager .next a")

        next_page = int(paging["href"].split("/")[-2]) if paging else None

    return [parse_quote(quote) for quote in quotes]


def write_to_csv(filename: str, quotes: list[Quote]) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    result = get_quotes()
    write_to_csv(output_csv_path, result)


if __name__ == "__main__":
    main("quotes.csv")
