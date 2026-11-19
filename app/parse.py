import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup, Tag, ResultSet

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_one_page_quote(soup: Tag) -> ResultSet[Tag]:
    return soup.select(".quote")


def get_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")

    all_quotes = get_one_page_quote(soup)

    next_page = soup.select_one(".next")

    while next_page is not None:
        page = next_page.select_one("a")["href"]
        text = requests.get(f"{BASE_URL}{page}").content
        soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_one_page_quote(soup))
        next_page = soup.select_one(".next")

    return [parse_single(quote) for quote in all_quotes]


def parse_single(quotes: Tag) -> Quote:
    tags_data = quotes.select(".tag")
    tags = []
    for tag in tags_data:
        tags.append(tag.text)
    return Quote(
        text=quotes.select_one(".text").text,
        author=quotes.select_one(".author").text,
        tags=tags
    )


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
