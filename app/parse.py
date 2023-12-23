import csv
import re
from dataclasses import asdict, dataclass, fields
from typing import Iterator

from bs4 import BeautifulSoup, SoupStrainer
from requests import Response, request

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    @classmethod
    def to_field_list(cls) -> list[str]:
        return [field.name for field in fields(cls)]


def _clean_string(input_string: str) -> str:
    cleaned_string = re.sub(r"\s+", " ", input_string)
    return cleaned_string.strip()


def _extract_quotes(response: Response | None = None) -> Iterator[Quote]:
    soup = BeautifulSoup(
        response.text,
        "html.parser",
        parse_only=SoupStrainer("div", class_="quote"),
    )
    for item in soup:
        yield Quote(
            text=_clean_string(item.select_one(".text").text),
            author=item.select_one(".author").text,
            tags=[
                tag_element.text
                for tag_element in item.select_one(".tags").select(".tag")
            ],
        )


def request_quotes(limit: int = 30) -> list[Quote]:
    page = 1
    quotes = []
    while page <= limit:
        response = request("GET", f"{BASE_URL}/page/{page}")
        if response.status_code != 200:
            print(f"Parsing has been stopped. Page {page} does not exist.")
            break
        quotes.extend(_extract_quotes(response))
        page += 1
    return quotes


def main(output_csv_path: str) -> None:
    quotes = request_quotes()
    with open(output_csv_path, "w") as file:
        writer = csv.DictWriter(file, Quote.to_field_list())
        writer.writeheader()
        writer.writerows(asdict(quote) for quote in quotes)


if __name__ == "__main__":
    main("quotes.csv")
