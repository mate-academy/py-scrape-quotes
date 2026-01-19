import time
from urllib.parse import urljoin
import requests
from requests import HTTPError

from app.collector import collect_items
from app.data import COLUMNS
from app.file_manager import save_to_file


SITE_URL = "https://quotes.toscrape.com/"


def parse(path: str, url: str = SITE_URL, start_page: int = 1) -> None:
    page = start_page

    quotes = []

    while True:
        new_url = urljoin(url, f"page/{str(page)}")

        response = requests.get(new_url)
        try:
            response.raise_for_status()
        except HTTPError:
            break

        quotes_to_add = collect_items(response.content)
        if not quotes_to_add:
            break

        quotes.extend(quotes_to_add)
        page += 1
        time.sleep(1)

    save_to_file(path, COLUMNS, quotes)


def main(output_csv_path: str) -> None:
    parse(output_csv_path, SITE_URL)


if __name__ == "__main__":
    main("quotes.csv")
