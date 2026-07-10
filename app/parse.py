import csv
from dataclasses import dataclass, fields, astuple

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


BIOGRAPHY_CACHE = dict()


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class AuthorBiography:
    full_name: str
    day: int
    month: str
    year: int
    location: str
    description: str


FIELDS = [field.name for field in fields(Quote)]

FIELDS_AUTHOR = [field.name for field in fields(AuthorBiography)]


def get_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def get_single_page_quotes(quotes: list) -> list[Quote]:
    return [get_single_quote(quote) for quote in quotes]


def get_single_author_biography(
        author_biography: BeautifulSoup
) -> AuthorBiography:
    date = author_biography.select_one(".author-born-date").text.split()
    return AuthorBiography(
        full_name=author_biography.select_one(".author-title").text,
        day=date[1].rstrip(","),
        month=date[0],
        year=date[2],
        location=author_biography.select_one(".author-born-location").text,
        description=author_biography.select_one(".author-description").text,
    )


def get_authors_biography(quotes: BeautifulSoup) -> list[AuthorBiography]:
    biographies = []
    for quote in quotes:
        url_biography = BASE_URL + quote.select_one("span a").get("href")
        if (biography := BIOGRAPHY_CACHE.get(url_biography)) is not None:
            biographies.append(get_single_author_biography(biography))
        else:
            biography = requests.get(url_biography).content
            page_soup = BeautifulSoup(biography, "html.parser")
            BIOGRAPHY_CACHE[url_biography] = page_soup
            biographies.append(get_single_author_biography(page_soup))
    return biographies


def get_quote_list() -> tuple[list[Quote], list[AuthorBiography]]:
    url = BASE_URL
    all_quotes = []
    all_biographies = []
    while url:
        text = requests.get(url).content
        page_soup = BeautifulSoup(text, "html.parser")
        quotes = page_soup.select(".quote")
        quotes_page = get_single_page_quotes(quotes)
        all_biographies.extend(get_authors_biography(quotes))
        all_quotes.extend(quotes_page)
        next_btn = page_soup.select_one("li.next a")
        if next_btn:
            url = BASE_URL + next_btn.get("href")
        else:
            url = None
    return (all_quotes, all_biographies)


def main(output_csv_path: str) -> None:
    quotes, biographies = get_quote_list()
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])

    with open(
            "authors_biograph.csv",
            "w", encoding="utf-8",
            newline=""
    ) as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS_AUTHOR)
        writer.writerows([astuple(biograph) for biograph in biographies])


if __name__ == "__main__":
    main("quotes.csv")
