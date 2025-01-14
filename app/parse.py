from dataclasses import dataclass, fields, astuple
import csv
import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def get_next_page(page_soup: Tag) -> str | None:
    pagination = page_soup.select_one("li.next > a")
    if pagination:
        return pagination.attrs["href"]
    return None


def parse_single_quote(quote_soup: Tag) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text.strip(),
        author=quote_soup.select_one(".author").text.strip(),
        tags=[tag.text.strip() for tag in quote_soup.select(".tags a")]
    )


def scrape_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes_soup = page_soup.select(".quote")
    return [parse_single_quote(quote) for quote in quotes_soup]


def scrape_quotes() -> list[Quote]:
    response = requests.get(URL).content
    page_soup = BeautifulSoup(response, "html.parser")
    all_quotes = scrape_single_page_quotes(page_soup)
    next_page = get_next_page(page_soup)

    while next_page:
        response = requests.get(f"{URL}{next_page}").content
        page_soup = BeautifulSoup(response, "html.parser")
        all_quotes.extend(scrape_single_page_quotes(page_soup))
        next_page = get_next_page(page_soup)

    return all_quotes


def write_to_file(quotes: list[Quote], file_name: str) -> None:
    with open(file_name, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = scrape_quotes()
    write_to_file(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
