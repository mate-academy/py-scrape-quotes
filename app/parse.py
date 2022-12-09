from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup, Tag
import csv
from urllib.parse import urljoin


MAIN_PAGE = "https://quotes.toscrape.com/"


@dataclass
class Author:
    lib = []
    name: str
    born_date: str
    born_location: str
    biography: str


PRODUCT_FIELDS_AUTHORS = [field.name for field in fields(Author)]
with open("Authors.csv", "a", encoding="utf-8") as quotes:
    writer = csv.writer(quotes)
    writer.writerow(PRODUCT_FIELDS_AUTHORS)
    quotes.close()


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


PRODUCT_FIELDS = [field.name for field in fields(Quote)]

with open("quotes.csv", "a", encoding="utf-8") as quotes:
    writer = csv.writer(quotes)
    writer.writerow(PRODUCT_FIELDS)
    quotes.close()


def parse_single_quote(soup: Tag) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=soup.select_one(".tags").text[32:].split())


def find_another_page(soup: BeautifulSoup) -> str:
    pagination = soup.find("li", class_="next").find("a")
    return pagination.get("href")


def find_authors_url(soup: BeautifulSoup) -> list:
    filt_for_quote = soup.select("div.quote span a")
    new_list = []
    for i in filt_for_quote:
        author_url = i.get("href")
        if author_url not in Author.lib:
            new_list.append(author_url)
    print(f"total authors in library {len(new_list)}")
    return new_list


def parse_authors(url: str) -> Author:
    print("start authors")
    request = requests.get(url)
    soup_authors = BeautifulSoup(request.content, "html.parser")
    domain = find_authors_url(soup_authors)
    for author in domain:
        link = urljoin(url, author)
        request = requests.get(link)
        soup_authors = BeautifulSoup(request.content, "html.parser")
        author_info = soup_authors.select_one(".author-details")
        return Author(
            name=soup_authors.select_one(
                "h3.author-title").text.split("\n")[0],
            born_date=author_info.select_one(
                "span.author-born-date").text,
            born_location=author_info.select_one(
                "span.author-born-location").text,
            biography=author_info.select_one(
                "div.author-description"
            ).text)


def main(output_csv_path: str, url: str = None) -> None:
    request_for_page = requests.get(url)
    soup = BeautifulSoup(request_for_page.content, "html.parser")
    need_to_parse = soup.select(".col-md-8 .quote")
    all_quote = [parse_single_quote(quote) for quote in need_to_parse]
    save_to_csv(output_csv_path, all_quote)
    print(f"Parse {url} and takes {len(all_quote)} new quotes")
    all_authors = [parse_authors(url)]
    save_authors_to_csv("Authors.csv", all_authors)
    try:
        find_another_page(soup)
        new_page = find_another_page(soup)
        page = urljoin(MAIN_PAGE, new_page)
        return main(output_csv_path, page)
    except TypeError:
        print("no more pages")


def save_to_csv(output_csv_path: str, all_quote: [Quote]) -> None:
    with open(output_csv_path, "a", encoding="utf-8") as quote:
        write_quo = csv.writer(quote)
        write_quo.writerows([astuple(x) for x in all_quote])
        quotes.close()


def save_authors_to_csv(output_csv_path: str, all_authors: [Author]) -> None:
    with open(output_csv_path, "a", encoding="utf-8") as author:
        writer_author = csv.writer(author)
        writer_author.writerows([astuple(author) for author in all_authors])
        quotes.close()


if __name__ == "__main__":
    print(main("quotes.csv", MAIN_PAGE))
