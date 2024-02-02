import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


@dataclass
class AuthorsBiography:
    name: str
    biography: str


AUTHORS_BIOGRAPHY_FIELDS = [field.name for field in fields(AuthorsBiography)]


def parse_single_quote(quoter_soup: BeautifulSoup) -> list:
    author_href = quoter_soup.select_one("div a")["href"]
    text = quoter_soup.select_one('span.text[itemprop="text"]').get_text(
        strip=True
    )
    author = quoter_soup.select_one("span > small").get_text(strip=True)
    tags = [
        tag.get_text(strip=True)
        for tag in quoter_soup.find_all("a", class_="tag")
    ]
    return [Quote(text=text, author=author, tags=tags), author_href]


def get_content_from_url(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Request failed with status code {response.status_code}")


def parse_authors_biography(author_href: set) -> list[AuthorsBiography]:
    list_authors = []
    for link in list(author_href):
        url = BASE_URL + link
        content = get_content_from_url(url)
        soup = BeautifulSoup(content, "html.parser")
        name = soup.select_one(".author-title").get_text(strip=True)
        biography = soup.select_one(".author-description").get_text(strip=True)
        result = AuthorsBiography(name=name, biography=biography)
        list_authors.append(result)
    return list_authors


def get_items_some_page(num_page: int) -> list:
    quote_list = []
    author_href = set()
    url = BASE_URL + "/page/{num_page}/".format(num_page=num_page)
    content = get_content_from_url(url)
    soup = BeautifulSoup(content, "html.parser")
    all_div_quote = soup.find_all("div", class_="quote")
    for div in all_div_quote:
        one_quote, one_author = parse_single_quote(div)
        quote_list.append(one_quote)
        author_href.add(one_author)
    return [quote_list, author_href]


def get_items_all_pages() -> list:
    num_page = 1
    all_quotes = []
    all_authors = set()
    while True:
        result = get_items_some_page(num_page)
        if result == [[], set()]:
            break  # No more pages

        all_quotes.extend(result[0])
        all_authors.update(result[1])
        num_page += 1

    return [all_quotes, all_authors]


def write_csv(path: str, items: list, column_headings: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as file:
        quote_writer = csv.writer(file)
        quote_writer.writerow(column_headings)
        quote_writer.writerows([astuple(quote) for quote in items])


def main(output_csv_path: str) -> None:
    items, authors_href = get_items_all_pages()
    write_csv("result.csv", items, QUOTE_FIELDS)
    authors_biography = parse_authors_biography(authors_href)
    write_csv(
        "author_biography.csv", authors_biography, AUTHORS_BIOGRAPHY_FIELDS
    )


if __name__ == "__main__":
    main("quotes.csv")
