import csv
from dataclasses import dataclass
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, Tag


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single(quote: Tag) -> Quote:
    text = quote.select_one(".text").text.strip()
    author = quote.select_one(".author").text.strip()
    tag_elements = quote.select(".tag")
    tags = [tag.text.strip() for tag in tag_elements]
    return Quote(text=text, author=author, tags=tags)


def get_quotes_from_page(page_soup: Tag) -> list[Quote]:
    quote_elements = page_soup.select(".quote")
    return [parse_single(quote) for quote in quote_elements]


def has_next_page(page_soup: Tag) -> bool:
    next_button = page_soup.select_one(".next > a")
    return next_button is not None


def get_all_quotes() -> list[Quote]:

    all_quotes = []
    current_url = BASE_URL

    while True:
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")
        quotes = get_quotes_from_page(soup)
        all_quotes.extend(quotes)
        if not has_next_page(soup):
            break
        next_link = soup.select_one(".next > a").get("href")
        current_url = urljoin(BASE_URL, next_link)

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_path: str) -> None:
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            tags_str = ", ".join(quote.tags)
            writer.writerow([quote.text, quote.author, tags_str])


def main(output_csv_path: str) -> None:
    all_quotes = get_all_quotes()
    write_quotes_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
