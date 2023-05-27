import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"
QUOTE_FIELDS = ["text", "author", "tags"]


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = quote_soup.select(".tags > a.tag")
    tag_list = [tag.text for tag in tags]
    return Quote(
        text=quote_soup.select_one(".quote > .text").text,
        author=quote_soup.select_one("small.author").text,
        tags=tag_list,
    )


def get_next_page_url(page_soup: BeautifulSoup) -> str | None:
    pager = page_soup.find("li", class_="next")
    if pager is None:
        return None
    next_link = pager.find("a", href=True)["href"].split("/")[-2]
    return BASE_URL + f"/page/{next_link}/"


def get_home_soup() -> list[Quote]:
    base_url = BASE_URL
    quotes = []

    while base_url:
        page = requests.get(base_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes.extend(soup.select(".quote"))
        base_url = get_next_page_url(soup)
        if base_url is None:
            break

    return [parse_single_quote(quote_soup) for quote_soup in quotes]


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)

        parse_list = get_home_soup()
        for parse in parse_list:
            writer.writerow([parse.text, parse.author, parse.tags])


if __name__ == "__main__":
    main("quotes.csv")
