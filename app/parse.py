from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_first_last_page(output_csv_path, soup):
    with open(output_csv_path, "a", encoding="utf-8") as quotes:
        for quote in soup.select(".quote"):
            quotes.write(str(
                Quote(text=quote.select_one(".quote .text").text,
                      author=quote.select_one(".quote .author").text,
                      tags=[
                          tag.text
                          for tag in quote.select(".quote .tags .tag")],
                      ))
            )
            quotes.write("\n")


authors_set = set()


def authors_biography(author_name, page):
    if author_name not in authors_set:
        with open("authors-details.csv", "a", encoding="utf-8") as authors:
            authors_set.add(author_name)
            page = requests.get(f"{BASE_URL}{page}").content
            soup = BeautifulSoup(page, "html.parser")
            authors.write(soup.select_one(".author-details").text)
            authors.write("\n")


def main(output_csv_path: str) -> None:
    page = requests.get(BASE_URL).content
    soup = BeautifulSoup(page, "html.parser")
    parse_first_last_page(output_csv_path, soup)

    with open(output_csv_path, "a", encoding="utf-8") as quotes:
        while soup.select_one(".next"):
            page_numb = soup.select_one(".next a")["href"]
            page = requests.get(f"{BASE_URL}{page_numb}").content
            soup = BeautifulSoup(page, "html.parser")
            for quote in soup.select(".quote"):
                quotes.write(str(
                    Quote(text=quote.select_one(".quote .text").text,
                          author=quote.select_one(".quote .author").text,
                          tags=[
                              tag.text
                              for tag in quote.select(".quote .tags .tag")],
                          ))
                )
                quotes.write("\n")
                authors_biography(quote.select_one(".author").text,
                                  quote.select_one("a")["href"])
        parse_first_last_page(output_csv_path, soup)


if __name__ == "__main__":
    main("quotes.csv")
