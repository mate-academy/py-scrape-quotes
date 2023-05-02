import csv
from dataclasses import dataclass, fields, astuple

from bs4 import BeautifulSoup, element
import requests


URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_single_quote(quote_info: element.Tag) -> Quote:

    return Quote(
        text=quote_info.select_one(".text").text,
        author=quote_info.select_one(".author").text,
        tags=[tag.text for tag in quote_info.select(".tag")]
    )


def get_single_page(soup: BeautifulSoup) -> list[Quote]:

    return [
        get_single_quote(quote_info) for quote_info in soup.select(".quote")
    ]


def parser() -> list[Quote]:
    request = requests.get(URL)
    soup = BeautifulSoup(request.text, "html.parser")
    page_url = soup.select_one("ul.pager > li.next > a")["href"]

    quote_list = get_single_page(soup)

    while True:
        request = requests.get(URL + page_url)
        soup = BeautifulSoup(request.text, "html.parser")
        quote_list.extend(get_single_page(soup))
        try:
            page_url = soup.select_one("ul.pager > li.next > a")["href"]
        except TypeError:
            break
    return quote_list


def main(output_csv_path: str) -> None:
    quotes = parser()
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
