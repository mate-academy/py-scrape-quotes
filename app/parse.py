import csv
import time
from dataclasses import dataclass, astuple, fields

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class BiographyAuthor:
    name: str
    born: str
    description: str


BASE_URL = "https://quotes.toscrape.com/"
QUOTES_FIELDS = [field.name for field in fields(Quote)]
BIO_AUTH_FIELDS = [field.name for field in fields(BiographyAuthor)]
AUTHORS = set()


def write_fields_name_csv(output_csv_path: str, class_fields: [str]) -> None:
    with open(output_csv_path, "a", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(class_fields)


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")],
    )


def parse_single_biography(soup: BeautifulSoup) -> BiographyAuthor:
    return BiographyAuthor(
        name=soup.select_one(".author-title").text,
        born=f"{soup.select_one('.author-born-date').text} "
        f"{soup.select_one('.author-born-location').text}",
        description=soup.select_one(".author-description").text,
    )


def get_soup(url: str, session: requests.Session) -> BeautifulSoup:
    response = session.get(url)
    return BeautifulSoup(response.content, features="html.parser")


def get_single_page_quotes(soup: BeautifulSoup) -> [Quote]:
    all_quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in all_quotes]


def write_csv(output_csv_path: str, data: [object]) -> None:
    with open(output_csv_path, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        for item in data:
            writer.writerow(astuple(item))


def get_author_bio(
    author_url: str, session: requests.Session
) -> BiographyAuthor:
    soup = get_soup(author_url, session)
    return parse_single_biography(soup)


def parse_author_bios(
    quotes: list[Quote],
    soup: BeautifulSoup,
    session: requests.Session,
    output_csv_path_bio: str,
) -> None:
    for _ in quotes:
        bio_link = soup.select_one(".quote a[href*='/author/']")
        author_url = f"{BASE_URL}{bio_link['href']}"
        if author_url not in AUTHORS:
            AUTHORS.add(author_url)
            bio = get_author_bio(author_url, session)
            write_csv(output_csv_path_bio, [bio])


def parse_all_site(
    output_csv_path_quote: str, output_csv_path_bio: str
) -> None:
    write_fields_name_csv(output_csv_path_quote, QUOTES_FIELDS)
    write_fields_name_csv(output_csv_path_bio, BIO_AUTH_FIELDS)

    session = requests.Session()
    num_page = 1

    while True:
        url_page = f"{BASE_URL}/page/{num_page}"
        soup = get_soup(url_page, session)
        quotes = get_single_page_quotes(soup)

        if not quotes:
            break

        write_csv(output_csv_path_quote, quotes)
        parse_author_bios(quotes, soup, session, output_csv_path_bio)
        num_page += 1
        time.sleep(1)


def main(
    output_csv_path: str, output_csv_path_bio: str = "output_csv_path_bio.csv"
) -> None:
    parse_all_site(output_csv_path, output_csv_path_bio)


if __name__ == "__main__":
    main("quotes.csv")
