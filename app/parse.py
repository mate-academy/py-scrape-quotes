import requests
import csv
from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin


from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


TAGS_FIELDS = (field.name for field in fields(Quote))


def parse_text(text: Tag) -> Quote:
    return (Quote(
        text=text.select_one(".text").text,
        author=text.select_one(".author").text,
        tags=[tag.get_text(strip=True) for tag in text.select(".tag")],
    ))


def get_next_page(soup: BeautifulSoup) -> str | None:
    next_link = soup.select_one("li.next a")
    if next_link:
        return next_link["href"]
    return None


def get_single_quote(page_soup: Tag) -> list[Quote]:
    texts = page_soup.select(".quote")
    return [parse_text(text) for text in texts]


def get_quotes() -> list[Quote]:
    quotes: list[Quote] = []
    url = BASE_URL
    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        quotes.extend(get_single_quote(soup))

        next_page = get_next_page(soup)
        url = urljoin(BASE_URL, next_page) if next_page else None

    return quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(TAGS_FIELDS)
        writer.writerows(astuple(quote) for quote in quotes)


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("result.csv")
