import csv
from dataclasses import dataclass
from typing import Generator

import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def page_generator(url: str) -> Generator[bytes, None, None]:
    my_url = url
    counter = 1
    while my_url:
        response = requests.get(my_url)
        yield response.content

        soup = BeautifulSoup(response.content, "html.parser")
        next_button = soup.find("li", class_="next")
        if next_button:
            next_page = next_button.find("a")["href"]
            counter += 1

            my_url = f"{url}page/{counter}/" \
                if "catalogue" not in my_url else \
                my_url.rsplit("/", 1)[0] + "/" + next_page
        else:
            my_url = None


def parse_quotes(page_content: bytes) -> list[Quote]:
    quotes = []
    soup = BeautifulSoup(page_content, "html.parser")
    html_quotes = soup.find_all("div", class_="quote")
    for html_quote in html_quotes:
        quotes.append(
            Quote(
                text=html_quote.find("span", class_="text").text,
                author=html_quote.find("small", class_="author").text,
                tags=[
                    tag.text for tag in html_quote.find_all("a", class_="tag")
                ],
            )
        )
    return quotes


def scrape_quotes() -> list[Quote]:
    quotes = []
    for page in page_generator(URL):
        quotes.extend(parse_quotes(page))
    return quotes


def write_to_file(quotes: list[Quote], output_file: str) -> None:
    try:
        with open(output_file, "a", newline="") as csvfile:
            fieldnames = ["text", "author", "tags"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for quote in quotes:
                writer.writerow({
                    "text": quote.text,
                    "author": quote.author,
                    "tags": quote.tags,
                })
    except (PermissionError, IOError) as e:
        print("Can't save quotes to file")
        print(e)


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    write_to_file(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
