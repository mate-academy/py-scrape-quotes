import csv
from dataclasses import dataclass, fields, astuple
from requests import request
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_page(base_url: str, page_num: int) -> BeautifulSoup:
    url = BASE_URL + f"/page/{page_num}/"
    page = request("get", url).content
    soup = BeautifulSoup(page, "html.parser")
    return soup


def get_quotes_soup(soup: BeautifulSoup) -> list:
    quotes = soup.select("div.quote")
    return quotes


def parse_quote(quote_soup: BeautifulSoup) -> Quote:
    quote = Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )
    return quote


def get_next_page(next_page: int, page: BeautifulSoup = None) -> int | None:
    if page and not page.select(".next"):
        next_page = None
    else:
        next_page += 1
        print(next_page)
    return next_page


def get_all_quotes() -> list[Quote]:
    next_page = 0
    all_quotes = []
    next_page = get_next_page(next_page)
    while next_page:
        page = get_page(BASE_URL, next_page)
        quotes_soup = get_quotes_soup(page)
        quotes = [parse_quote(quote) for quote in quotes_soup]
        all_quotes.extend(quotes)
        next_page = get_next_page(next_page, page)

    return all_quotes


def write_quotes(quotes_list: [Quote], output_path: str) -> None:
    with open(output_path, "a+", encoding="utf-8", newline="") as quotes_file:
        writer = csv.writer(quotes_file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(
            [quote for quote in [astuple(quote) for quote in quotes_list]]
        )


def main(output_csv_path: str) -> None:
    quotes_list = get_all_quotes()
    write_quotes(quotes_list, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
