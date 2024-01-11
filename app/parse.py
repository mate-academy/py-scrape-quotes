import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

import requests
from bs4 import Tag, BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_quotes() -> tuple[list[Quote], list[list[str]]]:
    page_num = 1
    all_quotes = []
    biography_links = []

    while True:

        page = requests.get(urljoin(BASE_URL, f"page/{page_num}/")).content
        soup = BeautifulSoup(page, "html.parser")

        quotes = soup.select(".quote")

        if quotes == []:
            break

        if quotes != []:

            biography_links.extend(
                [
                    quote_soup.select_one("a[href^='/author/']")["href"]
                    for quote_soup in quotes
                ]
            )

            all_quotes.extend(
                [parse_single_quote(quote_soup) for quote_soup in quotes]
            )

            page_num += 1

    biography_links = [
        [urljoin(BASE_URL, link)] for link in list(set(biography_links))
    ]
    return all_quotes, biography_links


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def write_biography_links_to_csv(biography_links: list[list[str]]) -> None:
    with open(
            "author_biography_links.csv", "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["Author biography link"])
        writer.writerows(biography_links)


def main(output_csv_path: str) -> None:
    quotes, biography_links = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)
    write_biography_links_to_csv(biography_links)


if __name__ == "__main__":
    main("quotes.csv")
