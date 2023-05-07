from dataclasses import dataclass
from bs4 import BeautifulSoup as bs
import requests

WEBSITE_URL = "http://quotes.toscrape.com"
TOTAL_PAGES = 10


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def scrape_quotes_from_page(page_url):
    quotes = []
    response = requests.get(page_url)
    soup = bs(response.text, "html.parser")
    for quote in soup.find_all("div", class_="quote"):
        text = quote.find("span", class_="text").text
        author = quote.find("small", class_="author").text
        tags = [tag.text for tag in quote.find_all("a", class_="tag")]
        quotes.append(Quote(text, author, tags))
    return quotes


def scrape_quotes():
    quotes = []
    for page_number in range(1, TOTAL_PAGES + 1):
        print(f"Scraping page {page_number}...")
        page_url = f"{WEBSITE_URL}/page/{page_number}"
        quotes.extend(scrape_quotes_from_page(page_url))
    return quotes


def save_quotes(output_csv_path, quotes):
    with open(output_csv_path, "w") as f:
        f.write("text,author,tags\n")
        for quote in quotes:
            f.write(f"{quote.text},{quote.author},{','.join(quote.tags)}\n")


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    save_quotes(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
