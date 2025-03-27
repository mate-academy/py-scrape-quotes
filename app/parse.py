import requests
import csv
from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def safe_cp1252(string: str) -> str:
    return string.encode("cp1252", errors="replace").decode("cp1252")


def extract_quotes_from_page(page_url: str) -> list[Quote]:
    response = requests.get(page_url)
    if response.status_code != 200:
        print(
            f"Failed to retrieve {page_url}: "
            f"Status code {response.status_code}"
        )
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    quotes = []
    for quote in soup.find_all("div", class_="quote"):
        text = quote.find("span", class_="text").get_text()
        author = quote.find("small", class_="author").get_text()
        tags = [tag.get_text() for tag in quote.find_all("a", class_="tag")]
        quotes.append(Quote(text=text, author=author, tags=tags))
    return quotes


def get_next_page(soup: BeautifulSoup) -> str | None:
    next_button = soup.find("li", class_="next")
    if next_button:
        next_page_url = next_button.find("a")["href"]
        return f"https: //quotes.toscrape.com{next_page_url}"
    return None


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com"
    current_url = base_url
    all_quotes = []

    while current_url:
        print(f"Scraping {current_url}...")
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, "html.parser")
        quotes = extract_quotes_from_page(current_url)
        all_quotes.extend(quotes)
        current_url = get_next_page(soup)

    with open(
            output_csv_path, mode="w", newline="", encoding="cp1252"
    ) as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in all_quotes:
            text = safe_cp1252(quote.text)
            author = safe_cp1252(quote.author)
            tags = safe_cp1252(str(quote.tags))
            writer.writerow([text, author, tags])

    print(f"Data has been written to {output_csv_path}")


if __name__ == "__main__":
    main("quotes.csv")
