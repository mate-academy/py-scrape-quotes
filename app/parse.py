import csv
from dataclasses import dataclass
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_page_content(url: str) -> BeautifulSoup:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_quotes_from_page(soup: BeautifulSoup) -> list[Quote]:
    quotes = []
    for quote_div in soup.find_all("div", class_="quote"):
        text = quote_div.find("span", class_="text").get_text(strip=True)
        author = quote_div.find("small", class_="author").get_text(strip=True)
        tags = [
            tag.get_text(strip=True)
            for tag in quote_div.find_all("a", class_="tag")
        ]
        quotes.append(Quote(text, author, tags))
    return quotes


def get_next_page_url(soup: BeautifulSoup, base_url: str) -> str:
    next_button = soup.find("li", class_="next")
    if next_button and next_button.find("a"):
        return urljoin(base_url, next_button.a["href"])
    return None


def scrape_all_quotes(base_url: str) -> list[Quote]:
    all_quotes = []
    current_url = base_url
    while current_url:
        soup = get_page_content(current_url)
        if not soup:
            break

        all_quotes.extend(parse_quotes_from_page(soup))

        current_url = get_next_page_url(soup, base_url)

        import time
        time.sleep(1)

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            writer.writerow([quote.text, quote.author, str(quote.tags)])


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com"
    quotes = scrape_all_quotes(base_url)
    write_quotes_to_csv(quotes, output_csv_path)
    print(f"Successfully scraped {len(quotes)} quotes to {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
