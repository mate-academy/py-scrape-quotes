import csv
from dataclasses import dataclass, fields
from bs4 import BeautifulSoup, Tag
import requests

BASE_URL = "https://quotes.toscrape.com/"

authors_cache = {}


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


REPLACEMENTS = [
    (" ", "-"),
    (". ", "-"),
    (".", "-"),
    (" .", "-"),
    ("'", ""),
    ("é", "e"),
]

QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_quotes(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def normalized_author_name(author_name: str) -> str:
    for old, new in REPLACEMENTS:
        author_name = (author_name.replace(old, new)
                       .replace("--", "-").strip("-"))
    return author_name


def get_author_biography(author_name: str) -> str:
    if author_name in authors_cache:
        return authors_cache[author_name]

    normalized_name = normalized_author_name(author_name)
    author_url = f"{BASE_URL}/author/{normalized_name}/"
    try:
        response = requests.get(author_url)
        soup = BeautifulSoup(response.content, "html.parser")

        biography = soup.select_one(".author-description").text.strip()
        authors_cache[author_name] = biography
        return biography
    except Exception as e:
        print(f"Error retrieving biography for {author_name}: {e}")
        return "No biography available (parsing error)"


def get_num_pages(page_soup: Tag) -> int:
    num_pages = 1
    while True:
        pager = page_soup.select_one(".pager")
        next_button = pager.select_one(".next a")

        if next_button:
            next_url = next_button["href"]
            next_page_content = requests.get(BASE_URL + next_url).content
            page_soup = BeautifulSoup(next_page_content, "html.parser")
            num_pages += 1
        else:
            break

    return num_pages


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [parse_quotes(quote) for quote in quotes]


def get_page_quotes() -> list[Quote]:
    text = requests.get(BASE_URL).content
    first_page_soup = BeautifulSoup(text, "html.parser")

    # num of pages
    all_quotes = get_single_page_quotes(first_page_soup)
    num_pages = get_num_pages(first_page_soup)

    for page_num in range(2, num_pages + 1):
        next_url = f"/page/{page_num}/"
        text = requests.get(BASE_URL + next_url).content
        next_page_soup = BeautifulSoup(text, "html.parser")
        all_quotes.extend(get_single_page_quotes(next_page_soup))
    return all_quotes


def parse_quote(quote: Quote) -> dict:
    author = quote.author
    biography = get_author_biography(author)

    return {
        "text": quote.text,
        "author": author,
        "biography": biography,
        "tags": quote.tags
    }


def write_to_csv(data: list[dict], filename: str, fields: list[str]) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def main(output_csv_path: str, authors_csv_path: str = None) -> None:
    all_quotes = get_page_quotes()
    quotes_data = [parse_quote(quote) for quote in all_quotes]

    write_to_csv(quotes_data, output_csv_path,
                 ["text", "author", "biography", "tags"])
    if authors_csv_path:
        authors_data = [{"author": author, "biography": biography}
                        for author, biography in authors_cache.items()]
        write_to_csv(authors_data, authors_csv_path, ["author", "biography"])


if __name__ == "__main__":
    output_csv_path = "quotes.csv"
    authors_csv_path = "authors.csv"
    main(output_csv_path, authors_csv_path)
