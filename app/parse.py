import csv
from dataclasses import dataclass, astuple

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_one_quote(quote_soup: Tag) -> Quote:
    text = quote_soup.select_one("span.text").text
    author = quote_soup.select_one("small.author").text
    tags_soup = quote_soup.select("div.tags > a.tag")
    tags = [tag.text for tag in tags_soup]

    return Quote(
        text=text,
        author=author,
        tags=tags
    )


def parse_one_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes_soup = page_soup.select("div.quote")

    return [get_one_quote(quote_soup) for quote_soup in quotes_soup]


def get_all_quotes() -> list[Quote]:
    all_quotes = []
    first_response = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(first_response, "html.parser")

    all_quotes.extend(parse_one_page(first_page_soup))

    next_page = first_page_soup.select_one("li.next > a")

    while next_page:
        next_url = BASE_URL + next_page["href"]
        response = requests.get(next_url).content
        page_soup = BeautifulSoup(response, "html.parser")
        all_quotes.extend(parse_one_page(page_soup))
        next_page = page_soup.select_one("li.next > a")

    return all_quotes


def write_quotes_to_csv(csv_path: str, quotes: list[Quote]) -> None:
    fields = ("text", "author", "tags")
    with open(csv_path, "w", newline="", encoding="utf-8") as result_file:
        csv_writer = csv.writer(result_file)
        csv_writer.writerow(fields)
        csv_writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(csv_path=output_csv_path, quotes=quotes)


if __name__ == "__main__":
    main("quotes.csv")
