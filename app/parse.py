import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


URL = "https://quotes.toscrape.com/"
QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = quote_soup.select_one(".keywords")["content"]
    tags = tags.split(",") if len(tags) > 0 else []
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=tags,
    )


def parse_singe_page(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def write_quotes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def check_next_page(soup: BeautifulSoup) -> None | str:
    next_page = soup.select_one(".next > a")
    return next_page["href"] if next_page else None


def parse_site() -> list[Quote]:
    page = requests.get(URL).content
    soup = BeautifulSoup(page, "html.parser")
    all_quotes = parse_singe_page(soup)
    next_page = check_next_page(soup)
    while next_page:
        page = requests.get(f"{URL}{next_page}").content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(parse_singe_page(soup))
        next_page = check_next_page(soup)
    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = parse_site()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
