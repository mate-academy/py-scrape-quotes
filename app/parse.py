import csv
import logging
import re
import sys
import requests
import unicodedata
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"
AUTHOR_URL = urljoin(BASE_URL, "author/")
AUTHOR_FILE = "authors.csv"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Author:
    fullname: str
    born_date: str
    born_location: str
    description: str


QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_FIELDS = [field.name for field in fields(Author)]

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("pars.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

AUTHORS_CACHE = set()


def slugify_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    nfkd_form = unicodedata.normalize("NFKD", name)
    name = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    name = name.replace(
        "'", ""
    ).replace(
        ".", "-"
    ).replace(" ", "-")
    return re.sub(r"-+", "-", name).strip("-")


def create_quote(data: Tag) -> Quote:
    text = data.select_one(".text").text
    author_name = data.select_one(".author").text
    tags = [tag.text for tag in data.select(".tag")]

    if not text or not author_name:
        logging.warning("No text or author_name found")
        raise ValueError(f"Data: {text}, {author_name}")

    AUTHORS_CACHE.add(slugify_name(author_name))

    return Quote(
        text=text,
        author=author_name,
        tags=tags,
    )


def scrap_single_page(url: str, session: requests.Session) -> list[Quote]:
    logging.info(f"Scraping page: {url}")
    response = session.get(url)

    if response.status_code == 404:
        return []
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    return [create_quote(quote_data) for quote_data in soup.select(".quote")]


def scrap_author_page(url: str, session: requests.Session) -> Author | None:
    logging.info(f"Scraping author: {url}")
    response = session.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    details = soup.select_one(".author-details")

    if not details:
        logging.warning(f"Author details not found at {url}")
        return None

    fullname = details.select_one(".author-title").text.strip(),
    born_date = details.select_one(".author-born-date").text.strip(),
    born_location = details.select_one(".author-born-location").text.strip(),
    description = details.select_one(".author-description").text.strip(),

    if not born_location or not born_date or not description or not fullname:
        logging.warning(f"Author details not found at {url}")
        raise ValueError(f"Data: {fullname}, {born_date}, "
                         f"{born_location}, {description}")

    return Author(
        fullname=details.select_one(".author-title").text.strip(),
        born_date=details.select_one(".author-born-date").text.strip(),
        born_location=details.select_one(".author-born-location").text.strip(),
        description=details.select_one(".author-description").text.strip(),
    )


def write_data_to_file(
        data: list,
        fields_row: list[str],
        file_name: str
) -> None:
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(fields_row)
        writer.writerows(astuple(d) for d in data)


def main(output_csv_path: str) -> None:
    with requests.Session() as session:
        all_quotes = []
        page = 1
        while True:
            url = urljoin(BASE_URL, f"page/{page}/")
            scraped_quotes = scrap_single_page(url, session)
            if not scraped_quotes:
                break
            all_quotes.extend(scraped_quotes)
            page += 1

        author_details = []
        for author_name in AUTHORS_CACHE:
            slug = slugify_name(author_name)
            author_url = urljoin(AUTHOR_URL, f"{slug}/")
            author_info = scrap_author_page(author_url, session)
            if author_info:
                author_details.append(author_info)

    logging.info(
        f"Success! Quotes: {len(all_quotes)}, Authors: {len(author_details)}")
    write_data_to_file(all_quotes, QUOTE_FIELDS, output_csv_path)
    write_data_to_file(author_details, AUTHOR_FIELDS, AUTHOR_FILE)


if __name__ == "__main__":
    main("quotes.csv")
