import sys
import csv
import time
import random
from dataclasses import dataclass, fields, astuple
import requests
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("parser.log"),
        logging.StreamHandler(sys.stdout)
    ],
)


BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]

biographies = dict()


def get_soup(url: str) -> BeautifulSoup:
    """Fetch page content, check response, and return BeautifulSoup object."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/119.0 Safari/537.36"
        )
    }

    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.content, "html.parser")

            logging.info(f"Fetched successfully: {url}")
            time.sleep(random.uniform(0.5, 1.5))  # ввічлива пауза
            return soup

        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt + 1}/3 failed for {url}: {e}")
            if attempt < 2:
                time.sleep(2)
            else:
                logging.error(f"All attempts failed for {url}")
                raise


def add_biography(url: str, author: str) -> None:
    soup = get_soup(url)
    born = soup.select_one(".author-born-date")
    born = born.text if born else None
    description = soup.select_one(".author-description")
    description = description.text if description else None
    if born or description:
        biographies[author] = born, description


def get_from_page(url: str) -> tuple[list[Quote], str | None]:
    soup = get_soup(url)
    raw_quotes = soup.select(".quote")
    quotes = []

    for quote in raw_quotes:
        text = quote.select_one(".text")
        text = text.text if text else None
        author = quote.select_one(".author")
        author = author.text if author else None
        tags = [tag.text for tag in quote.select(".tag")]
        if author and text:
            quotes.append(Quote(text=text, author=author, tags=tags))

        if author and author not in biographies.keys():
            logging.info(f"Try to get {author} biography")
            link_tag = quote.select_one("a")
            href = link_tag.get("href") if link_tag else None
            if href is not None:
                bio_url = urljoin(url, href)
                logging.info(f"bio url {bio_url} to biography")
                add_biography(bio_url, author)
                logging.info(f"{author} biography added to cash")
            else:
                logging.info(f"no link for {author} to biography page")

    element_next = soup.select_one(".next a")
    if element_next:
        next_page_href = element_next["href"]
    else:
        logging.info(f"This is the last page {url}")
        next_page_href = None
    return quotes, next_page_href


def get_all_data(url: str) -> list[Quote]:
    logging.info(f"Getting data from {url} (first page)")
    quotes, next_page_href = get_from_page(url)
    while next_page_href is not None:
        next_page_url = urljoin(BASE_URL, next_page_href)
        logging.info(f"Getting data from {next_page_url}")
        new_quotes, next_page_href = get_from_page(next_page_url)
        quotes.extend(new_quotes)
    return quotes


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    logging.info("Writing quotes to csv")
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        # далі tags записується у вигляді списку за вимогами завдання і тестів
        writer.writerows(astuple(quote) for quote in quotes)


def write_biographies_to_csv(bio: dict, path: str) -> None:
    logging.info(f"Writing biographies to {path}")
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(("author", "born", "description"))
        for author, data in bio.items():
            writer.writerow((author, data[0], data[1]))


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_all_data(BASE_URL), output_csv_path)
    write_biographies_to_csv(biographies, "bio.csv")


if __name__ == "__main__":
    main("quotes.csv")
