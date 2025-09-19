from dataclasses import dataclass, fields, astuple
import csv

import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com/page/"

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTES_NAME = [field.name for field in fields(Quote)]


def parse_single_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags .tag")]
    )


def get_num_pages():
    page = 1
    while True:
        url = f"https://quotes.toscrape.com/page/{page}/"
        response = requests.get(url)
        if "No quotes found!" in response.text:
            print(f"Пагинация закончилась на странице {page}")
            break
        else:
            page += 1
    return page - 1


def get_pages():
    page = 1
    text = requests.get(URL).content
    first_soup = BeautifulSoup(text, "html.parser")
    all_quotes = get_single_page_quotes(first_soup)
    for x in range(1, get_num_pages() + 1):
        url = "https://quotes.toscrape.com/page/" + str(x) + "/"
        response = requests.get(url).content
        next_page_soup = BeautifulSoup(response, "html.parser")
        all_quotes.extend(get_single_page_quotes(next_page_soup))
        print(url)
        print(page)
        page += 1
    return all_quotes


def get_single_page_quotes(page_soup: Tag):
    quotes = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTES_NAME)
        writer.writerows([astuple(quote) for quote in get_pages()])


if __name__ == "__main__":
    get_num_pages()
    main("quotes.csv")
