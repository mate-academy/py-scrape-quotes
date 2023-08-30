import csv
import requests

from dataclasses import dataclass, astuple, fields

from bs4 import BeautifulSoup


QUOTES_BASE_URL = "https://quotes.toscrape.com/"
AUTHORS_DICT = {}


@dataclass
class Quote:
    text: str
    author: str
    author_bio: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_bio(quote_description_link: str, author_name: str) -> str:
    page = requests.get(quote_description_link).content
    soup = BeautifulSoup(page, "html.parser")
    if not AUTHORS_DICT.get(author_name):
        AUTHORS_DICT[author_name] = soup.select_one(".author-description").text

    return AUTHORS_DICT[author_name]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one(".author").text,
        author_bio=parse_single_bio(
            QUOTES_BASE_URL + quote_soup.select_one("span > a")["href"],
            quote_soup.select_one(".author").text
        ),
        tags=[tag.text for tag in quote_soup.select("a.tag")],
    )


def get_quotes() -> list[Quote]:
    quotes = []
    for i in range(1, 11):
        page = requests.get(QUOTES_BASE_URL + f"/page/{i}/").content
        soup = BeautifulSoup(page, "html.parser")

        quotes_soup = soup.select(".quote")

        quotes.extend([parse_single_quote(quote_soup) for quote_soup in quotes_soup])
    return quotes


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_quotes(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
