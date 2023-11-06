import requests
from bs4 import BeautifulSoup

from dataclasses import dataclass

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    print(dict(
        quote=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=quote_soup.select(".keywords")[0]["content"].split(",")
    ))


def get_home_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    quotes = soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def main():
    get_home_quotes()

# def main(output_csv_path: str) -> None:
#     get_home_quotes()


if __name__ == "__main__":
    main()
    # main("quotes.csv")
