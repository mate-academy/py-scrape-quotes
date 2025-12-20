from dataclasses import dataclass, astuple
from urllib.parse import urljoin
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

def quote_list_parser(soup_page):
    quotes = soup_page.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]

def get_all_quotes():
    all_quotes = []
    current_url = HOME_URL
    
    while True:
        print(f"Parsing: {current_url}")
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")

        all_quotes.extend(quote_list_parser(soup))

        next_btn = soup.select_one(".pager .next > a")
        
        if next_btn:
            next_path = next_btn["href"]
            current_url = urljoin(HOME_URL, next_path)
        else:
            print("End.")
            break
    return all_quotes

def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("result.csv")
