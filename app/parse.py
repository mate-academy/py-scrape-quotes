import csv
from dataclasses import dataclass, asdict

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").get_text(strip=True)
    author = quote_soup.select_one(".author").get_text(strip=True)
    tags = [tag.get_text(strip=True) for tag in quote_soup.select(".tag")]

    return Quote(text=text, author=author, tags=tags)


def parse_quotes_page() -> [Quote]:
    page_num = 1
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select(".quote")
    print(f"Page {page_num}")

    while soup.select_one(".next"):
        page = requests.get(
            BASE_URL + soup.select_one(".next > a")["href"]
        ).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(soup.select(".quote"))

        if soup.select_one(".next > a"):
            page_num = (
                int(soup.select_one(".next > a")["href"].split("/")[-2]) - 1
            )
            print(f"Page {page_num}")

        # last page
        if page_num > 1 and soup.select_one(".next > a") is None:
            print(f"Page {page_num + 1}")

    return [parse_single_quote(quote) for quote in quotes]


def write_quotes_to_csv(filename: str, quotes: list) -> None:
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["text", "author", "tags"])
        writer.writeheader()

        for quote in quotes:
            quote_to_dict = asdict(quote)
            quote_to_dict["tags"] = str(quote_to_dict["tags"])
            writer.writerow(quote_to_dict)


def main(output_csv_path: str) -> None:
    quotes = parse_quotes_page()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
