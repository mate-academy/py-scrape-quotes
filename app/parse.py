import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


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


def parse_single_quote(quote: Tag) -> [Quote]:
    tags_str = quote.select_one("meta.keywords")["content"]
    tags = [t for t in tags_str.split(",") if t]
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags
    )


def parse_quotes() -> list:
    num_pages = get_num_pages()
    result = []
    for page_num in range(1, num_pages + 1):
        resp = requests.get(f"{BASE_URL}page/{page_num}/")
        soup = BeautifulSoup(resp.text, "html.parser")
        quotes = soup.select(".quote")
        result.extend(parse_single_quote(q) for q in quotes)
    return result


def write_to_csv(output_csv_path: str, quotes: [Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_to_csv(output_csv_path, parse_quotes())


if __name__ == "__main__":
    main("quotes.csv")
