import csv
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    """
    A data class representing a quote.

    Attributes:
        text (str): The text of the quote.
        author (str): The author of the quote.
        tags (str): A string of tags associated with the quote.
    """
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    """
    Parses a single quote from the BeautifulSoup object.

    Args:
        quote_soup (BeautifulSoup): A BeautifulSoup object containing the
                                    quote HTML.

    Returns:
        Quote: An instance of the Quote dataclass containing the quote's
               text, author, and tags.
    """
    text = quote_soup.select_one(".text").get_text()
    author = quote_soup.select_one(".author").get_text()
    tags = [tag.get_text() for tag in quote_soup.select(".tags .tag")]

    return Quote(text=text, author=author, tags=tags)


def get_single_page_quotes(page: BeautifulSoup) -> list[Quote]:
    """
    Parses all quotes from a single page of quotes.

    Args:
        page (BeautifulSoup): A BeautifulSoup object containing the page
                              HTML.

    Returns:
        list[Quote]: A list of Quote objects parsed from the page.
    """
    quotes = page.select(".quote")
    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    """
    Retrieves quotes from all pages of the website with pagination.

    The function iterates through the pages of the website until it
    encounters a page without quotes or a 404 error, indicating there
    are no more pages to retrieve.

    Returns:
        list[Quote]: A list of Quote objects parsed from all pages of
                     quotes.
    """
    all_quotes = []
    page_number = 1

    while True:
        response = requests.get(f"{BASE_URL}page/{page_number}/")

        if response.status_code == 404:
            break

        page = BeautifulSoup(response.content, "html.parser")
        quotes_on_page = get_single_page_quotes(page)

        if not quotes_on_page:
            break

        all_quotes.extend(quotes_on_page)
        page_number += 1

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], filename: str) -> None:
    """
    Writes the quotes to a CSV file.

    Args:
        quotes (list[Quote]): A list of Quote objects to be written to
                              the CSV.
        filename (str): The name of the CSV file to write the quotes to.
    """
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


def main(quotes_csv_path: str) -> None:
    """
    Main function to get quotes and write them to a CSV file.

    Args:
        quotes_csv_path (str): The path to the output quotes CSV file.
    """
    quotes = get_quotes()

    write_quotes_to_csv(quotes, quotes_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
