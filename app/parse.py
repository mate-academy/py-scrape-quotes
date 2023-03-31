import csv
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def scrape_quotes_and_authors(
        url: str, quote_writer: csv.DictWriter, author_writer: csv.DictWriter
) -> set:
    page_num = 1
    authors = set()

    while True:
        page = requests.get(url.format(page_num)).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        if not quotes:
            break
        for quote in quotes:
            text = quote.select_one(".text").text.strip()
            author_elem = quote.select_one(".author")
            author = author_elem.text.strip()
            author_link = author_elem.find_next_sibling("a")["href"]
            tags = [tag.text.strip() for tag in quote.select(".tag")]
            quote_writer.writerow(
                {"text": text, "author": author, "tags": tags}
            )

            if author_link not in authors:
                authors.add(author_link)
                author_page = requests.get(
                    f"https://quotes.toscrape.com{author_link}"
                ).content
                author_soup = BeautifulSoup(author_page, "html.parser")
                author_description = author_soup.select_one(
                    ".author-description"
                ).text.strip()
                author_writer.writerow(
                    {"author": author, "about": author_description}
                )
        page_num += 1

    return authors


def write_quotes_and_authors(output_csv_path: str) -> None:
    url = "https://quotes.toscrape.com/page/{}/"

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile, \
            open("authors.csv", "w", newline="", encoding="utf-8") as author:
        quote_fieldnames = ["text", "author", "tags"]
        quote_writer = csv.DictWriter(csvfile, fieldnames=quote_fieldnames)
        quote_writer.writeheader()

        author_fieldnames = ["author", "about"]
        author_writer = csv.DictWriter(
            author, fieldnames=author_fieldnames
        )
        author_writer.writeheader()

        authors = scrape_quotes_and_authors(url, quote_writer, author_writer)

        print(f"{len(authors)} authors scraped.")


def main(output_csv_path: str) -> None:
    write_quotes_and_authors(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
