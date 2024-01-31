from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://quotes.toscrape.com/'


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quotes(quoter_soup: BeautifulSoup) -> Quote:
    print(dict(
        text=quoter_soup.select_one('span.text').get_text(strip=True),
        author=quoter_soup.select_one('span>small').get_text(strip=True),
        tags=[tag.get_text(strip=True) for tag in quoter_soup.find_all('a', class_='tag')]
    ))


def get_quotes() -> list[Quote]:
    response = requests.get(BASE_URL).content
    soup = BeautifulSoup(response, "html.parser")
    quotes = soup.find_all("div", class_="quote")
    print(quotes)
    return [parse_single_quotes(quoter_soup) for quoter_soup in quotes]


def main(output_csv_path: str) -> None:
    get_quotes()


if __name__ == "__main__":
    main("quotes.csv")
