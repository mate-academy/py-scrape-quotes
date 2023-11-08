import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

URL = "http://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_one_page(soup: BeautifulSoup) -> list[Quote]:
    quotes = soup.select(".quote")
    all_quotes = []

    for quote in quotes:
        text = quote.select_one(".text").get_text()
        author = quote.select_one(".author").get_text()
        tags = quote.select_one(".tags").select(".tag")
        tags_list = [tag.get_text() for tag in tags]
        quote = Quote(text, author, tags_list)
        all_quotes.append(quote)

    return all_quotes


def main(output_csv_path: str) -> None:
    response = requests.get(URL).text
    soup = BeautifulSoup(response, "html.parser")
    all_quotes = parse_one_page(soup)

    while soup.select_one(".next"):
        next_page = soup.select_one(".next").select_one("a").get("href")
        next_url = f"{URL}{next_page[1:]}"
        response = requests.get(next_url).text
        soup = BeautifulSoup(response, "html.parser")
        all_quotes.extend(parse_one_page(soup))

    write_to_csv(all_quotes, output_csv_path)


def write_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
