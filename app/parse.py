import csv
from dataclasses import dataclass, astuple

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def scrape_single_quote(quote):
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.get_text() for tag in quote.select(".tags .tag")],
    )


def scrape_page():
    current_url = BASE_URL
    all_quotes = []
    while current_url:
        text = requests.get(current_url).text
        soup = BeautifulSoup(text, "html.parser")
        quotes_on_page = soup.select(".quote")
        all_quotes.extend(quotes_on_page)

        next_li = soup.select_one(".next")
        if next_li:
            next_url = next_li.select_one("a")["href"]
            current_url = BASE_URL + next_url
        else:
            current_url = None

    return [scrape_single_quote(quote) for quote in all_quotes]


def write_to_csv(quotes, output_csv_path):
    with open(output_csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    write_to_csv(scrape_page(), output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
