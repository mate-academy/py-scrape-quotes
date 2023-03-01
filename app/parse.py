from typing import Any
from app.writer_csv import (write_to_csv,
                            save_to_csv,
                            Author,
                            Quote)

import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin

MAIN_PAGE = "https://quotes.toscrape.com/"


def parse_single_quote(soup: Tag) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=soup.select_one(".tags").text[32:].split()
    )


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
    return new_list


def parse_authors(url: str) -> [Author]:
    request = requests.get(url)
    soup_authors = BeautifulSoup(request.content, "html.parser")
    domain = find_authors_url(soup_authors)
    list_authors = []
    for author in domain:
        link = urljoin(url, author)
        request = requests.get(link)
        soup_authors = BeautifulSoup(request.content, "html.parser")
        author_info = soup_authors.select_one(".author-details")
        list_authors.append(Author(
            name=soup_authors.select_one(
                "h3.author-title").text.split("\n")[0],
            born_date=author_info.select_one(
                "span.author-born-date").text,
            born_location=author_info.select_one(
                "span.author-born-location").text,
            biography=author_info.select_one(
                "div.author-description"
            ).text))
    return list_authors


def main(output_csv_path: str) -> None:
    write_to_csv(output_csv_path)
    parse_with_recurtion(output_csv_path, MAIN_PAGE)


def parse_with_recurtion(output_csv_path: str, url: str = None) -> Any:
    request_for_page = requests.get(url)
    soup = BeautifulSoup(request_for_page.content, "html.parser")
    need_to_parse = soup.select(".col-md-8 .quote")
    all_quote = [parse_single_quote(quote) for quote in need_to_parse]
    save_to_csv(output_csv_path, all_quote)
    all_authors = parse_authors(url)
    save_to_csv("Authors.csv", all_authors)
    try:
        page = urljoin(MAIN_PAGE, find_another_page(soup))
        return parse_with_recurtion(output_csv_path, page)
    except AttributeError:
        print("no more pages")


if __name__ == "__main__":
    main("quotes.csv")
