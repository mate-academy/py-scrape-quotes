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
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one("span.text").text.replace("\n", ""),
        author=quote_soup.select_one(".author").text.replace("\n", ""),
        tags=[tag.text for tag in quote_soup.select("a.tag")],
    )


def get_quotes() -> list[Quote]:
    quotes = []
    for i in range(1, 11):
        page = requests.get(QUOTES_BASE_URL + f"/page/{i}/").content
        soup = BeautifulSoup(page, "html.parser")

        quotes_soup = soup.select(".quote")

        quotes.extend(
            [parse_single_quote(quote_soup) for quote_soup in quotes_soup]
        )
    return quotes


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def remove_double_newlines(filename: str) -> None:
    with open(filename, "r", encoding="utf-8") as file:
        content = file.read()
    new_content = content.replace("\n\n", "\n")

    with open(filename, "w", encoding="utf-8") as file:
        file.write(new_content)


def main(output_csv_path: str) -> None:
    write_quotes_to_csv(get_quotes(), output_csv_path)
    remove_double_newlines(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
