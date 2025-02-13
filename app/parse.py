import time
from dataclasses import dataclass, asdict, fields
from bs4 import BeautifulSoup
import requests
import csv

BASE_URL = "https://quotes.toscrape.com/"


# soup = BeautifulSoup(html_doc, 'html.parser')


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Biography:
    name: str
    born: str
    description: str


def parse_main_page(page: str, authors: dict) -> [Quote]:
    page_list = []
    check = True
    i = 0
    soup = 0
    while check:
        i += 1
        page_ = page + "page/" + str(i)
        html_doc = requests.get(page_).content
        soup = BeautifulSoup(html_doc, 'html.parser')
        if not soup.find("li", class_="next"):
            check = False
        for div_quote in soup.find_all("div", class_="quote"):
            text = div_quote.find("span", class_="text").string
            author = div_quote.find("small", class_="author").string
            biography_link = div_quote.find("a")["href"]
            div_tags = [quote.string for quote in div_quote.find("div").find_all("a")]
            if not authors.get(author):
                authors[author] = BASE_URL + biography_link[1:]
            page_list.append(Quote(text=text, author=author, tags=div_tags))
    return page_list


def parse_author_page(authors: dict) -> [Biography]:
    data = []
    for author in authors.values():
        html_doc = requests.get(author).content
        soup = BeautifulSoup(html_doc, "html.parser")
        name = soup.find("h3").string
        born = soup.find("span", class_="author-born-date").string
        description = soup.find("div", class_="author-description").string.strip()
        data.append(Biography(name=name, born=born, description=description))
    return data


def manage_main_page_file(file: str, data: list[Quote]) -> None:
    with open(file, "w", newline='') as csvfile:
        fieldnames = [field.name for field in fields(Quote)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([asdict(quote) for quote in data])


def manage_biographie_pages(file: str, data: list[Biography]) -> None:
    with open(file, "w") as csvfile:
        fieldnames = [field.name for field in fields(Biography)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([asdict(quote) for quote in data])


def main(output_csv_path1: str, output_csv_path2: str) -> None:
    authors = {}
    data1 = parse_main_page(BASE_URL, authors)
    data2 = parse_author_page(authors)
    manage_main_page_file(output_csv_path1, data1)
    manage_biographie_pages(output_csv_path2, data2)


# parse_page(BASE_URL)


if __name__ == "__main__":
    main("quotes.csv", "biographies.csv")
