import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/page/{}/"
QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=[tag.text.strip() for tag in quote.select("div.tags a")]
    )


def get_single_page_quotes(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.select("div.quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_num_pages(page_soup: BeautifulSoup) -> int:
    pagination = page_soup.select_one(".pager")
    if not pagination:
        return 1
    pages = pagination.select("li")
    if len(pages) < 2:
        return 1
    return int(pages[-2].text.strip())


def get_quotes() -> list[Quote]:
    all_quotes = []
    page_number = 1

    while True:
        url = BASE_URL.format(page_number)
        response = requests.get(url)
        if response.status_code != 200:
            break

        page_soup = BeautifulSoup(response.content, "html.parser")
        quotes = get_single_page_quotes(page_soup)
        all_quotes.extend(quotes)

        next_button = page_soup.select_one(".pager .next a")
        if not next_button:
            break

        page_number += 1

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    quotes_list = get_quotes()
    write_quotes_to_csv(quotes_list, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
