from dataclasses import dataclass, fields, astuple
import csv
import requests
from bs4 import BeautifulSoup


HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(product: BeautifulSoup) -> Quote:
    return Quote(
        text=product.select_one(".text").text,
        author=product.select_one(".author").text,
        tags=[tag.text for tag in product.select("a.tag")],
    )


def get_quotes() -> list[Quote]:
    text = requests.get(HOME_URL).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    recived_quotes = [parse_single_quote(quote) for quote in quotes]
    if soup.select_one(".next"):
        while soup.select_one(".next"):
            next_ = soup.select_one(".next").select_one("a").get("href")
            text = requests.get(f"{HOME_URL}{next_}").content
            soup = BeautifulSoup(text, "html.parser")
            quotes = soup.select(".quote")
            for quote in quotes:
                recived_quotes.append(parse_single_quote(quote))
    return recived_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(f"{output_csv_path}", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")