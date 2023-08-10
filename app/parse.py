import csv
from dataclasses import dataclass, fields
from bs4 import BeautifulSoup
import requests

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".quote > span.text").text
    author = quote_soup.select_one(".author").text
    tags_elements = quote_soup.select(".tags > a")

    tags_list = [tag_element.text for tag_element in tags_elements]

    return Quote(
        text=text,
        author=author,
        tags=tags_list
    )


def get_num_pages() -> int:
    base_url = "https://quotes.toscrape.com/page/1/"
    page_number = 1

    while True:
        response = requests.get(base_url)
        response.raise_for_status()

        page_soup = BeautifulSoup(response.content, "html.parser")

        next_link = page_soup.select_one("li.next")
        if next_link:
            page_number += 1
            base_url = f"https://quotes.toscrape.com/page/{page_number}/"
        else:
            break

    return page_number


def get_quotes_for_page(page_number: int) -> list[Quote]:
    page_url = f"https://quotes.toscrape.com/page/{page_number}/"
    response = requests.get(page_url)
    response.raise_for_status()

    page_soup = BeautifulSoup(response.content, "html.parser")
    quotes = page_soup.select(".quote")

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    num_pages = get_num_pages()

    all_quotes = []
    for page_num in range(1, num_pages + 1):
        all_quotes.extend(get_quotes_for_page(page_num))

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows(
            [quote.text, quote.author, quote.tags] for quote in quotes
        )


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
