import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quotes(quotes: Tag) -> Quote:
    return Quote(
        text=quotes.select_one(".text").text,
        author=quotes.select_one(".author").text,
        tags=[tag.text for tag in quotes.select(".tag")]
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quotes(quote) for quote in quotes]


def get_home_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quotes(quote) for quote in quotes]


def get_all_quotes() -> list[Quote]:
    url = BASE_URL
    all_quotes = []
    page_count = 0
    while url:
        page_count += 1
        html = requests.get(url).content
        soup = BeautifulSoup(html, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        next_link = soup.select_one("li.next a")
        if next_link:
            url = urljoin(BASE_URL, next_link["href"])
        else:
            break
    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
