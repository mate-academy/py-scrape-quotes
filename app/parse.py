import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup, ResultSet, Tag


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELD = [field.name for field in fields(Quote)]


def get_text_quotes(inform: Tag) -> str:
    return inform.select_one(".text").text


def get_author_quotes(inform: Tag) -> str:
    return inform.select_one(".author").text


def get_tags_quotes(inform: Tag) -> list[str]:
    tags = inform.select(".tag")
    return [tag.text for tag in tags]


def create_list_of_quotes(pages: list[ResultSet[Tag]]) -> list[Quote]:
    quotes = []
    for page in pages:
        for information in page:
            quotes.append(
                Quote(
                    text=get_text_quotes(information),
                    author=get_author_quotes(information),
                    tags=get_tags_quotes(information
                                         )
                )
            )
    return quotes


def get_quotes_from_all_pages(
        soup: BeautifulSoup,
        url: str
) -> list[ResultSet[Tag]]:
    all_quotes_from_pages = []
    while soup.select("li.next"):
        all_quotes_from_pages.append(soup.select(".quote"))
        page = soup.select_one("li.next > a")["href"]
        soup = BeautifulSoup(requests.get(url + page).content, "html.parser")
    all_quotes_from_pages.append(soup.select(".quote"))
    return all_quotes_from_pages


def main(output_csv_path: str) -> None:
    url = "https://quotes.toscrape.com"
    page = requests.get(url).content
    soup = BeautifulSoup(page, "html.parser")

    quotes = create_list_of_quotes(get_quotes_from_all_pages(soup, url))

    with open(output_csv_path, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELD)
        writer.writerows([astuple(quote) for quote in quotes])


if __name__ == "__main__":
    main("quotes.csv")
