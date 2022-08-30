import csv
import requests

from dataclasses import dataclass, astuple
from bs4 import BeautifulSoup
from tqdm import tqdm

HOME_PAGE = "https://quotes.toscrape.com/"
QUOTE_FIELDS = ["text", "author", "tags"]


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags_soup = quote_soup.select(".tags")
    tags = [tag.text.replace("Tags:", "").split() for tag in tags_soup][0]

    return Quote(text=text, author=author, tags=tags)


def get_single_page_quote(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quote() -> list[Quote]:
    page = requests.get(HOME_PAGE).content
    first_page_soup = BeautifulSoup(page, "html.parser")
    all_quote = get_single_page_quote(first_page_soup)

    for num_page in tqdm(range(2, 11)):
        page = requests.get(f"{HOME_PAGE}/page/{num_page}").content
        page_soup = BeautifulSoup(page, "html.parser")
        all_quote.extend(get_single_page_quote(page_soup))

    return all_quote


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        quotes = get_all_quote()
        writer.writerows(astuple(quote) for quote in quotes)


if __name__ == "__main__":
    main("quotes.csv")
