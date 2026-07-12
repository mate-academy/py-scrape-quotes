import csv
from dataclasses import dataclass, fields

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")],
    )


def get_author_bio_link(quote_soup: BeautifulSoup) -> str:
    about_link = quote_soup.select_one("small.author + a")
    return BASE_URL + about_link["href"]


def get_single_page_quotes(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_single_page_author_links(page_soup: BeautifulSoup) -> dict[str, str]:
    quotes = page_soup.select(".quote")
    return {
        quote_soup.select_one(".author").text: get_author_bio_link(quote_soup)
        for quote_soup in quotes
    }


def get_all_quotes() -> tuple[list[Quote], dict[str, str]]:
    all_quotes = []
    author_links = {}
    session = requests.Session()

    page_url = BASE_URL
    while page_url:
        response = session.get(page_url)
        response.raise_for_status()
        page_soup = BeautifulSoup(response.content, "html.parser")

        all_quotes.extend(get_single_page_quotes(page_soup))
        author_links.update(get_single_page_author_links(page_soup))

        next_button = page_soup.select_one(".next > a")
        page_url = BASE_URL + next_button["href"] if next_button else None

    return all_quotes, author_links


def get_author_bio(session: requests.Session, author_url: str) -> str:
    response = session.get(author_url)
    response.raise_for_status()
    author_soup = BeautifulSoup(response.content, "html.parser")

    return author_soup.select_one(".author-description").text.strip()


def get_author_bios(author_links: dict[str, str]) -> dict[str, str]:
    session = requests.Session()
    return {
        author: get_author_bio(session, link)
        for author, link in author_links.items()
    }


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([field.name for field in fields(Quote)])
        writer.writerows(
            [(quote.text, quote.author, str(quote.tags)) for quote in quotes]
        )


def write_author_bios_to_csv(
    author_bios: dict[str, str], authors_csv_path: str
) -> None:
    with open(authors_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["author", "bio"])
        writer.writerows(author_bios.items())


def main(output_csv_path: str, authors_csv_path: str = "authors.csv") -> None:
    quotes, author_links = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)

    author_bios = get_author_bios(author_links)
    write_author_bios_to_csv(author_bios, authors_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
