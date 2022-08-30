import csv
import requests

from dataclasses import dataclass, astuple
from bs4 import BeautifulSoup
from tqdm import tqdm

HOME_PAGE = "https://quotes.toscrape.com/"

QUOTE_FIELDS = ["text", "author", "tags"]
AUTHOR_FIELDS = ["full name", "place of born", "date of born", "descriptions"]
AUTHORS_OUTPUT_CSV_PATH = "authors.csv"


@dataclass
class Author:
    full_name: str
    place_of_born: str
    date_of_born: str
    descriptions: str


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_detail_of_author(author_soup: BeautifulSoup) -> dict:
    date_of_born = author_soup.select_one(".author-born-date").text
    place_of_born = author_soup.select_one(".author-born-location").text
    descriptions = author_soup.select_one(".author-description").text

    return {
        "date_of_born": date_of_born,
        "place_of_born": place_of_born,
        "descriptions": descriptions
    }


def parse_single_author(author) -> dict:
    if author[-1] == ".":
        author = author[:-1]

    author = author.replace(". ", "-").replace(" ", "-").replace(".", "-").replace("é", "-").replace("'", "")

    page = requests.get(f"{HOME_PAGE}/author/{author}/").content
    page_soup = BeautifulSoup(page, "html.parser")
    return get_detail_of_author(page_soup)


all_authors = {}  # dictionary in which all information about the authors is stored


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags_soup = quote_soup.select(".tags")
    tags = [tag.text.replace("Tags:", "").split() for tag in tags_soup][0]

    if author not in all_authors:
        all_authors[author] = parse_single_author(author)

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


def get_all_authors() -> list[Author]:
    return [
        Author(
            full_name=author,
            place_of_born=all_authors[author]["place_of_born"],
            date_of_born=all_authors[author]["date_of_born"],
            descriptions=all_authors[author]["descriptions"]
        ) for author in all_authors
    ]


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w") as quote_file:
        writer = csv.writer(quote_file)
        writer.writerow(QUOTE_FIELDS)
        quotes = get_all_quote()
        writer.writerows(astuple(quote) for quote in quotes)

    with open(AUTHORS_OUTPUT_CSV_PATH, "w") as author_file:
        writer = csv.writer(author_file)
        writer.writerow(AUTHOR_FIELDS)
        authors = get_all_authors()
        writer.writerows(astuple(author) for author in authors)


if __name__ == "__main__":
    main("quotes.csv")
