import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quote(product_soup: Tag) -> Quote:
    tags = [product_soup.select_one(".tags > .keywords")["content"]]
    tags_with_spaces = []
    for tag in tags:
        if tag:
            tags_with_spaces.extend(tag.split(","))

    return Quote(
        text=product_soup.select_one("span.text").text,
        author=product_soup.select_one(".author").text,
        tags=tags_with_spaces
    )


def get_single_page_quotes(product_soup: BeautifulSoup) -> list[Quote]:
    quotes = product_soup.select(".quote")
    return [get_single_quote(quote) for quote in quotes]


def check_next_page(product_soup: BeautifulSoup) -> int:
    try:
        next_ = product_soup.select_one(".next > a")["href"].split("/")[-2]
        return int(next_)
    except TypeError:
        return 0


def get_quotes() -> list[Quote]:
    base_url = "https://quotes.toscrape.com/"
    page = requests.get(base_url).content
    soup = BeautifulSoup(page, "html.parser")
    next_page = check_next_page(soup)
    all_quotes = get_single_page_quotes(soup)

    while next_page:
        next_url = requests.get(f"{base_url}page/{next_page}/").content
        soup = BeautifulSoup(next_url, "html.parser")
        all_quotes.extend(get_single_page_quotes(soup))
        next_page = check_next_page(soup)

    return all_quotes


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    with open(output_csv_path, "w", encoding="UTF-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows(
            [[quote.text, quote.author, quote.tags] for quote in quotes]
        )


if __name__ == "__main__":
    main("quotes.csv")
