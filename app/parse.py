import csv
from dataclasses import dataclass, fields
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com"

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=[tag.text.strip() for tag in quote.select(".tag")]
    )


def get_next_page_url(soup: Tag) -> str | None:
    next_button = soup.select_one(".pager .next a")
    if next_button:
        return BASE_URL + next_button["href"]
    return None


def get_all_quotes() -> list[Quote]:
    quotes: list[Quote] = []
    url = BASE_URL

    while url:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        quote_tags = soup.select(".quote")

        for quote_tag in quote_tags:
            quotes.append(parse_single_quote(quote_tag))
        url = get_next_page_url(soup)

    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["Text", "Author", "Tags"])
        for quote in quotes:
            writer.writerow([
                quote.text,
                quote.author,
                ", ".join(quote.tags)
            ])


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
