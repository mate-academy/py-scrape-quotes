import csv
import requests

from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Bio:
    title: str
    description: str


def parse_single_bio(bio_soup: BeautifulSoup) -> Bio:
    return Bio(
        title=bio_soup.select_one(".author-title").text,
        description=bio_soup.select_one(".author-description").text,
    )


def get_bios(base_url: str) -> list[Bio]:
    from app.parse import get_quotes

    all_bios = []

    for author_url in set(
        quote.author_page_url for quote in get_quotes(base_url)
    ):
        bio_page = urljoin(base_url, author_url)
        bio_page_url = requests.get(bio_page).content
        bio_page_soup = BeautifulSoup(bio_page_url, "html.parser")
        author_details = bio_page_soup.select_one(".author-details")

        if author_details:
            bio = parse_single_bio(author_details)
            all_bios.append(bio)

    return all_bios


def write_bio_to_csv(bio_csv_path: str) -> None:
    # base_url = os.environ.get("BASE_URL")
    base_url = "https://quotes.toscrape.com/"

    with open(bio_csv_path, "w", encoding="utf-8", newline="") as bio_file:
        writer = csv.writer(bio_file, delimiter=";")

        writer.writerow(Bio.__annotations__.keys())
        bios = get_bios(base_url)

        for bio in bios:
            title = bio.title
            description = bio.description.strip()
            writer.writerow([title, description])
