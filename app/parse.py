from dataclasses import dataclass, astuple
from bs4 import BeautifulSoup
import requests
import csv

HOME_URL = "https://quotes.toscrape.com/"

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_single_quote(quote):
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags .tag")]
    )

def quote_list_parser():
    text = requests.get(HOME_URL).content
    soup = BeautifulSoup(text, "html.parser")
    quotes = soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]

def get_page_num(soup_page) -> int:
    pagination = soup_page.select(".pagination")
    if not pagination:
        return 1
    return int(pagination.select(".li")[-2].text)


def main(output_csv_path: str) -> None:
    quotes = quote_list_parser()
    
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("result.csv")
