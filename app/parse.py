import csv

import requests
from dataclasses import dataclass, fields
from bs4 import BeautifulSoup, Tag, ResultSet

URL_BASE = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


quote_fields = fields(Quote)
headers = [field.name for field in quote_fields]


def extract_tags(tags: ResultSet[Tag]) -> list[str]:
    return [tag.text for tag in tags]


def parse_single_quote(quote_tag: Tag) -> Quote:
    return Quote(
        text=quote_tag.select_one(".text").text,
        author=quote_tag.select_one(".author").text,
        tags=extract_tags(quote_tag.select(".tag"))
    )


def parse_quotes_per_page(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> list[Quote]:
    content = requests.get(URL_BASE).content
    page_soup = BeautifulSoup(content, "html.parser")
    all_quotes = parse_quotes_per_page(page_soup)

    while True:
        try:
            next_page_link = page_soup.select(".next")[0].find("a").get("href")
        except IndexError:
            break
        else:
            page = requests.get(URL_BASE + next_page_link).content
            page_soup = BeautifulSoup(page, "html.parser")
            all_quotes.extend(parse_quotes_per_page(page_soup))

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()

    data = [[quote.text, quote.author, quote.tags] for quote in quotes]

    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)


if __name__ == "__main__":
    main("quotes.csv")
