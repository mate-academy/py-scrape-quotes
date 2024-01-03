from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_next_page(page_soup: BeautifulSoup) -> BeautifulSoup | None:
    return page_soup.select_one("ul.pager > li.next")


def parse_page_quotes() -> list[Quote]:
    page = requests.get(BASE_URL).content
    page_soup = BeautifulSoup(page, "html.parser")
    quotes = []
    page_count = 1

    while page_soup:

        page_quotes = page_soup.select("div.quote")
        for quote in page_quotes:
            quotes.append(
                Quote(
                    text=quote.select_one(".text").text[1:-1],
                    author=quote.select_one(".author").text,
                    tags=[tag.text for tag in quote.select(".tag")]
                )
            )

        next_page_exist = get_next_page(page_soup)
        if page_soup:
            page_count += 1
            page = requests.get(BASE_URL, {"page": page_count}).content
            page_soup = BeautifulSoup(page, "html.parser")

    return quotes


def write_quote_to_csv(file_path: str, quotes: list[Quote]):
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["Text", "Author", "Tags"])

        for quote in quotes:
            writer.writerow(quote.text, quote.author, quote.tags)


def main(output_csv_path: str) -> None:
    quotes = parse_page_quotes()

    print(quotes)
    write_quote_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
