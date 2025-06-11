import csv
from dataclasses import dataclass

from bs4 import BeautifulSoup, Tag
import requests


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    def to_list(self) -> list[str]:
        return [self.text, self.author, str(self.tags)]


URL = "https://quotes.toscrape.com/"


def parse_quote_element(quote: Tag) -> Quote:
    text_element = quote.select_one(".text")

    text = None
    if text_element:
        text = text_element.text

    if text is None:
        raise ValueError("Quote text not found in the element")

    tags = [tag.text for tag in quote.select(".tag")]

    author = None
    author_element = quote.select_one(".author")
    if author_element:
        author = author_element.text

    if author is None:
        raise ValueError("Author not found in the element")

    return Quote(text=text, author=author, tags=tags)


def main(output_csv_path: str) -> None:
    current_page = 1
    quotes: list[Quote] = []

    while True:
        url = f"{URL}page/{current_page}/"

        response = requests.get(url)

        page = BeautifulSoup(response.content, "html.parser")

        quotes_elements = page.select(".quote")

        quotes.extend(
            [
                parse_quote_element(quote_element)
                for quote_element in quotes_elements
            ]
        )

        has_next = page.select_one("ul.pager > li.next")

        if has_next is None:
            break

        current_page += 1

    with open(
        output_csv_path, "w", encoding="utf-8-sig", newline=""
    ) as output_file:
        csv_writer = csv.writer(output_file, delimiter=",")

        csv_writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            csv_writer.writerow(quote.to_list())


if __name__ == "__main__":
    main("quotes.csv")
