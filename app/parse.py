import csv
import requests

from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, astuple, fields


HOME_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


FIELDS_FILE = [field.name for field in fields(Quote)]


def create_quote(post: Tag) -> Quote:
    return Quote(
        text=post.select_one(".text").text,
        author=post.select_one(".author").text,
        tags=[tag.text for tag in post.select(".tag")]
    )


def get_all_posts(home_url: str) -> list[Quote]:
    page = requests.get(home_url).content
    soup = BeautifulSoup(page, "html.parser")
    list_quote = []
    posts = soup.select(".quote")
    list_quote.extend([create_quote(post) for post in posts])
    while soup.find("li", {"class": "next"}):
        page = requests.get(
            home_url + f"{soup.select_one('.next > a')['href']}"
        ).content
        soup = BeautifulSoup(page, "html.parser")
        posts = soup.select(".quote")
        list_quote.extend([create_quote(post) for post in posts])

    return list_quote


def write_to_file(output_csv_path: str) -> None:
    list_quote = get_all_posts(HOME_URL)
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS_FILE)
        writer.writerows([astuple(quote) for quote in list_quote])


def main(output_csv_path: str) -> None:
    write_to_file(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
