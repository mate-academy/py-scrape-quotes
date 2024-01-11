import csv
from urllib.parse import urljoin

import requests
import bs4

from dataclasses import dataclass

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote: bs4) -> dict:
    return {
        "text": quote.select_one(".text").text,
        "author": quote.select_one(".author").text,
        "tags": [tag.text for tag in quote.select(".tag")]
    }


def parse_single_author(soup: bs4) -> dict:
    return {
        "name": soup.select_one(".author-title").text,
        "born_date": soup.select_one(".author-born-date").text,
        "born_location": soup.select_one(".author-born-location").text,
        "description": soup.select_one(".author-description").text
    }


def parse_single_page(page_soup: bs4) -> [dict]:
    return [
        parse_single_quote(quote) for quote in page_soup
    ]


def write_data_to_file(csv_file: str, data: list[dict]) -> None:
    with open(csv_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = data[0].keys()
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(data)


def paginate_by_pages() -> [dict]:
    request = requests.get(BASE_URL)
    soup = bs4.BeautifulSoup(request.content, "html.parser")
    data = parse_single_page(soup.select(".quote"))
    while soup.select_one(".next > a"):
        next_page = soup.select_one(".next > a").get("href")
        request = requests.get(urljoin(BASE_URL, next_page))
        soup = bs4.BeautifulSoup(request.content, "html.parser")
        data.extend(parse_single_page(soup.select(".quote")))
    return data


def create_links_from_authors(authors: [str]) -> [str]:
    authors = list(set(authors))
    authors_links = []
    for author in authors:
        author_link = author.replace(".", "-")
        author_link = author_link.replace(" ", "-")
        author_link = author_link.replace("'", "")
        author_link = author_link.replace("é", "e")
        author_link = author_link.strip("-")
        authors_links.append(author_link.replace("--", "-"))
    return authors_links


def parse_authors(authors_links: [str]) -> [dict]:
    authors_data = []
    for authors_link in authors_links:
        request = requests.get(urljoin(BASE_URL, "author/" + authors_link))
        soup = bs4.BeautifulSoup(request.content, "html.parser")
        authors_data.append(parse_single_author(soup))
    return authors_data


def main(output_csv_path: str) -> None:
    data = paginate_by_pages()
    write_data_to_file(output_csv_path, data)

    authors_links = create_links_from_authors(
        [quote_dict["author"] for quote_dict in data]
    )
    authors_data = parse_authors(authors_links)
    write_data_to_file("authors.csv", authors_data)


if __name__ == "__main__":
    main("quotes.csv")
