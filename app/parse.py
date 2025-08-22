from dataclasses import dataclass, fields, astuple
import csv
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags a")],
    )


def get_num_pages() -> int:

    page = 1

    while True:
        url = f"https://quotes.toscrape.com/page/{page}/"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        next_li = soup.find("li", class_="next")
        if next_li and next_li.a:
            page += 1
        else:
            break

    return int(page)


def get_single_page_quotes(page_soup: Tag) -> [Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_info() -> list:
    num_pages = get_num_pages()
    all_quotes = []

    for page_num in range(1, num_pages + 1):
        url = f"{BASE_URL}page/{page_num}/"
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

    return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: [Quote]) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        for quote in quotes:
            writer.writerow(astuple(quote))


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(output_csv_path, get_info())


if __name__ == "__main__":
    main("quotes.csv")
