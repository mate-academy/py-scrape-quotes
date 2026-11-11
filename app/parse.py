import csv
from dataclasses import dataclass, fields, astuple

import requests # noqa
from bs4 import BeautifulSoup # noqa


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


TITLE = [field.name for field in fields(Quote)]
BASE_URL = "https://quotes.toscrape.com/page/1/"


def parse_page() -> requests:
    page = 1
    url = BASE_URL
    while True:
        response = requests.get(url)
        if response.status_code != 200 or "No quotes found" in response.text:
            return
        yield response.content
        page += 1
        url = f"https://quotes.toscrape.com/page/{page}/"


def parse_content(byte: bytes) -> list:
    soup = BeautifulSoup(byte, "html.parser")
    result = []
    quotes = soup.select(".quote")

    for quote in quotes:
        result.append(
            Quote(
                text=quote.select_one(".text").text,
                author=quote.select_one(".author").text,
                tags=[tag.text for tag in quote.select("a.tag")]
            )
        )
    return result


def write_in_file(output_csv_path: str) -> None:
    all_quotes = []

    for data in parse_page():
        response = parse_content(data)
        all_quotes.extend([astuple(r) for r in response])

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(TITLE)
        writer.writerows(all_quotes)


def main(output_csv_path: str) -> None:
    write_in_file(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
