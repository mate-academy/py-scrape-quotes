import csv
from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def quote_parse(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.find(
        "span", {"class": "text"}
    ).text
    return Quote(
        text=text,
        author=quote_soup.find(
            "small", {"class": "author"}
        ).text,
        tags=[
            tag.text for tag in quote_soup.find_all(
                "a", {"class": "tag"}
            )
        ],
    )


def get_quotes() -> list[Quote]:
    quotes = []
    url = BASE_URL

    while url:
        response = requests.get(url)
        soup = BeautifulSoup(
            response.text, "html.parser"
        )

        quote_elements = soup.find_all(
            "div", {"class": "quote"}
        )
        quotes.extend(
            [
                quote_parse(quote) for quote in quote_elements
            ]
        )

        next_page = soup.find("li", {"class": "next"})
        url = (BASE_URL + next_page.find("a")["href"]) if next_page else None

    return quotes


def save_quotes_to_csv(
        quotes: list[Quote],
        output_csv_path: str
) -> None:
    with open(
            output_csv_path,
            mode="w", newline="",
            encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow(
                [quote.text, quote.author, quote.tags]
            )


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    save_quotes_to_csv(quotes, output_csv_path)
    print(f"Quotes saved in {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
    get_quotes()
