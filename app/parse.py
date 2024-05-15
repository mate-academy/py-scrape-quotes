import csv
from dataclasses import dataclass, astuple
from bs4 import BeautifulSoup, ResultSet, Tag
import requests


URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def parse_all_quotes_from_single_page(url: str) -> ResultSet[Tag]:
    page = requests.get(url)
    markup = BeautifulSoup(page.text, "html.parser")
    return markup.select(".quote")


def create_class_instance_from_markup(
        list_of_quotes_in_html: list
) -> list[Quote]:
    list_of_quotes_instances = []
    for quote in list_of_quotes_in_html:

        text = str(quote.select_one(".text").text)

        author = str(quote.select_one(".author").text)

        tags = quote.find_all("a", class_="tag")
        tag_list = [str(tag.text) for tag in tags]

        list_of_quotes_instances.append(
            Quote(
                text=text,
                author=author,
                tags=tag_list,
            )
        )
    return list_of_quotes_instances


def main(output_csv_path: str) -> None:
    quotes = []
    page_num = 1

    while True:
        all_quotes_from_page = parse_all_quotes_from_single_page(
            f"{URL}/page/{page_num}/"
        )
        if not all_quotes_from_page:
            break
        quotes += create_class_instance_from_markup(all_quotes_from_page)
        page_num += 1

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
