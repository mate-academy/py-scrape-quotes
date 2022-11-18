import csv
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from os.path import exists

BASE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

    def __iter__(self) -> iter:
        return iter([self.text, self.author, self.tags])


@dataclass
class Author:
    name: str
    biography: str

    def __str__(self) -> str:
        return self.name

    def __iter__(self) -> iter:
        return iter([self.name, self.biography])


def get_biography(link_to_author: str) -> str:
    page = requests.get(f"{BASE_URL}/{link_to_author}").content
    soup = BeautifulSoup(page, "html.parser")
    return soup.select_one(".author-details").text


def save_authors(authors: list[Author]) -> None:
    path_to_authors_csv = "authors.csv"
    mode = "w" if exists(path_to_authors_csv) else "x"
    with open(path_to_authors_csv,
              mode,
              10,
              "utf-8",
              newline="") as file_to_save:
        writer = csv.writer(file_to_save)
        writer.writerows(authors)
        file_to_save.close()


def get_quites(parse_authors: bool = False) -> list[Quote]:
    quites = []
    authors = []
    has_next = True
    num_page = 1
    while has_next:
        page = requests.get(f"{BASE_URL}/page/{num_page}").content
        soup = BeautifulSoup(page, "html.parser")
        blocks = soup.select(".quote")
        for block in blocks:
            text = block.select_one(".text").text
            author = block.select_one(".author").text
            if parse_authors:
                if len([author_ for author_ in authors
                        if author_.name == author]) == 0:
                    need_content = block.contents[3]
                    biography = get_biography(need_content.a.attrs["href"])
                    authors.append(Author(author, biography))
            tags = [tag.text for tag in block.select(".tag")]
            quites.append(Quote(text=text, author=author, tags=tags))
        has_next = soup.select_one(".next")
        num_page += 1

    if parse_authors:
        save_authors(authors)

    return quites


def main(output_csv_path: str) -> None:
    mode = "w" if exists(output_csv_path) else "x"
    with open(output_csv_path, mode, 100, "utf-8", newline="") as file_to_save:
        fieldnames = [" text", "author", "tags"]
        writer = csv.writer(file_to_save)
        writer.writerow(fieldnames)
        writer.writerows(get_quites(parse_authors=False))


if __name__ == "__main__":
    main("quotes.csv")
