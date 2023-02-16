import csv
import requests_cache

from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin
from bs4 import BeautifulSoup

session = requests_cache.CachedSession("cache")


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    about_author: str
    tags: list[str]


QUOTES_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(
        quote_soup: BeautifulSoup,
        home_url: str,
        session: requests_cache
) -> Quote:
    url_about_author = urljoin(
        home_url, quote_soup.select_one("span > a")["href"])
    page = session.get(url_about_author).content
    soup = BeautifulSoup(page, "html.parser")
    description = soup.select_one("div.author-description").text
    quote = Quote(
        text=quote_soup.select_one("span.text").text,
        author=quote_soup.select_one("span > small.author").text,
        about_author=description.lstrip(),
        tags=[
            tag_soup.text for tag_soup in quote_soup.select(
                "div.tags > a.tag")
        ]
    )
    return quote


def get_home_quotes() -> [Quote]:
    session = requests_cache.CachedSession(BASE_URL)
    page_first = session.get(BASE_URL).content
    soup = BeautifulSoup(page_first, "html.parser")
    quotes = soup.select(".quote")
    all_quotes = [
        parse_single_quote(
            quote_soup, BASE_URL, session) for quote_soup in quotes
    ]
    url_next_page = soup.select_one("nav > ul > li.next > a")["href"]
    while url_next_page:
        home_url = urljoin(BASE_URL, url_next_page)
        page = session.get(home_url).content
        soup = BeautifulSoup(page, "html.parser")
        quotes = soup.select(".quote")
        if soup.select_one("nav > ul > li.next"):
            url_next_page = soup.select_one("nav > ul > li.next > a")["href"]
        else:
            url_next_page = 0

        all_quotes.extend([
            parse_single_quote(
                quote_soup, home_url, session) for quote_soup in quotes
        ])

    return all_quotes


def write_qoutes_to_csv(quotes: [Quote], file_out_csv: str) -> None:
    with open(file_out_csv, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTES_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(file_out_csv: str) -> None:
    all_quotes = get_home_quotes()
    write_qoutes_to_csv(all_quotes, file_out_csv)


if __name__ == "__main__":
    main("quotes.csv")
