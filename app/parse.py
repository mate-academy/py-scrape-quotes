import csv
from dataclasses import dataclass, astuple

import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


URL = "https://quotes.toscrape.com"


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    tag_elements = quote.select(".tags .tag")
    tags = [tag.text for tag in tag_elements]

    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=tags
    )


def get_single_page_quotes(page: BeautifulSoup) -> [Quote]:
    quotes = page.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_all_quotes() -> [Quote]:
    all_quotes = []
    page_num = 1

    while True:
        print(page_num)
        url = f"{URL}/page/{page_num}"
        page = requests.get(url).content

        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))

        if soup.select_one(".next"):
            page_num += 1
        else:
            break

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()

    with open(output_csv_path, "w", encoding="UTF-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow(astuple(quote))


if __name__ == "__main__":
    main("quotes.csv")
