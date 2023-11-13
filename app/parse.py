import csv
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, fields, astuple

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def get_single_quote(soup: BeautifulSoup) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[
            tag.text for tag in soup.select(".tags .tag")
        ]
    )


def parse_single_page(soup: BeautifulSoup) -> list[Quote]:
    page = soup.select(".quote")
    return [get_single_quote(quote) for quote in page]


def check_next_page(page_soup: BeautifulSoup) -> bool:
    if page_soup.select_one(".next") is not None:
        return True
    return False


def get_all_quotes() -> list[Quote]:
    page_content = requests.get(BASE_URL).content
    soup = BeautifulSoup(page_content, "html.parser")
    all_pages = parse_single_page(soup)

    current_page = 2
    while check_next_page(soup):
        page_content = requests.get(
            BASE_URL + f"/page/{current_page}/"
        ).content
        soup = BeautifulSoup(page_content, "html.parser")
        all_pages.extend(parse_single_page(soup))
        current_page += 1

    return all_pages


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf8", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(QUOTES_FIELDS)
        csvwriter.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
