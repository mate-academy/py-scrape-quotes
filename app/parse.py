import csv
import requests

from dataclasses import dataclass, astuple, fields
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]
    # biography: dict[str: str]


URL = "https://quotes.toscrape.com/"
QUOTES_NAME = [field.name for field in fields(Quote)]


def get_author_biography(url: str) -> dict:
    page = requests.get(url).content
    author_biography_soup = BeautifulSoup(page, "html.parser")
    return dict(
        author_title=author_biography_soup.select_one(".author-title").text,
        author_born_date=author_biography_soup.select_one(
            ".author-born-date"
        ).text,
        author_born_location=author_biography_soup.select_one(
            ".author-born-location"
        ).text,
        author_description=author_biography_soup.select_one(
            ".author-description"
        ).text,
    )


def get_single_quote(quote_soup: BeautifulSoup) -> Quote:
    # author_biography_url = URL + (
    #     quote_soup.select_one("a").css.tag.attrs["href"].replace("/", "", 1)
    # )
    text = quote_soup.select_one(".text").text
    author = quote_soup.select_one(".author").text
    tags = quote_soup.select_one(".tags").text.split("\n")[3:-1]
    print(author)
    return Quote(
        text=text,
        author=author,
        tags=tags,
        # biography=get_author_biography(author_biography_url)
    )


def get_next_page_url(index: int) -> str:
    return URL + f"page/{index}/"


def get_list_of_all_quotes(page_index: int) -> [Quote]:
    if page_index == 1:
        page = requests.get(URL).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        return [get_single_quote(quote_soup) for quote_soup in quotes]
    else:
        next_page_url = get_next_page_url(page_index)
        page = requests.get(next_page_url).content
        soup = BeautifulSoup(page, "html.parser")
        next_quotes = soup.select(".quote")
        if next_quotes:
            return [get_single_quote(quote_soup) for quote_soup in next_quotes]
        return []


def write_quotes_to_csv(quotes: [Quote], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_NAME)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    page_index = 1
    result_quotes = []
    while page_index != 0:
        quotes_list = get_list_of_all_quotes(page_index)
        result_quotes.extend(quotes_list)
        if quotes_list:
            page_index += 1
        else:
            page_index = 0
            write_quotes_to_csv(result_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
