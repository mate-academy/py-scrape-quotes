import csv
import dataclasses
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


BASE_URL = "https://quotes.toscrape.com/"
QUOTE_FIELDS = [field.name for field in dataclasses.fields(Quote)]


def fetch_quotes() -> list[Quote]:
    collected_quotes = []
    page = 1
    while True:
        response = requests.get(f"{BASE_URL}page/{page}/")
        soup = BeautifulSoup(response.content, "html.parser")
        quotes_on_page = soup.select("div.quote")
        if not quotes_on_page:
            break

        for quote in quotes_on_page:
            collected_quotes.append(Quote(
                text=quote.select_one("span.text").text,
                author=quote.select_one("small.author").text,
                tags=[tag.text for tag in quote.select("div.tags a")]
            ))
        page += 1

    return collected_quotes


def save_quotes_to_csv(quotes: list[Quote], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([dataclasses.astuple(quote) for quote in quotes])


def main(file_path: str) -> None:
    save_quotes_to_csv(fetch_quotes(), file_path)


if __name__ == "__main__":
    main("quotes.csv")
