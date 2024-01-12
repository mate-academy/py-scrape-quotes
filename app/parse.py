import csv
from dataclasses import dataclass, fields, astuple


import requests
from bs4 import BeautifulSoup

URL = "https://quotes.toscrape.com/page/1/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_quote_fields(quote_class: Quote = Quote) -> list:
    return [field.name for field in fields(quote_class)]


def get_tags(tags_soup: BeautifulSoup) -> [str]:
    tags = tags_soup.select("a.tag")
    return [tag.text for tag in tags]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one("span.text").text,
        author=quote.select_one("small.author").text,
        tags=get_tags(quote.select_one("div.tags"))
    )


def parse_single_page(soup: BeautifulSoup) -> [Quote]:
    quotes = soup.select("div.quote")
    return [parse_single_quote(quote=quote) for quote in quotes]


def get_quotes() -> [Quote]:
    current_page = 1
    all_quotes = []
    while True:
        print(f"Page: #{current_page}")
        page = requests.get(
            f"https://quotes.toscrape.com/page/{current_page}/"
        ).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(parse_single_page(soup))
        current_page += 1
        if not soup.select("li.next"):
            break
    return all_quotes


def write_quotes_to_csv(quotes: [Quote], file_name: str) -> None:
    with open(file_name, "w") as file:
        writer = csv.writer(file)
        writer.writerow(get_quote_fields())
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(quotes=quotes, file_name=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
