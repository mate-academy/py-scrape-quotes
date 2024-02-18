import csv
from dataclasses import dataclass, fields, astuple
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELD = [field.name for field in fields(Quote)]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    text = quote.select_one("span.text").text.strip()
    author = quote.select_one("span > small.author").text.strip()
    tags = [tag.text.strip() for tag in quote.select("div.tags a")]
    return Quote(text, author, tags)


def get_single_page_quote(page_soup: BeautifulSoup) -> [Quote]:
    quotes = page_soup.find_all(class_="quote")

    return [parse_single_quote(quote) for quote in quotes]


def get_home_quotes() -> [Quote]:
    page = requests.get(BASE_URL).content
    first_page_quote = BeautifulSoup(page, "html.parser")

    all_quotes = get_single_page_quote(first_page_quote)

    for page_num in range(2, 100_000):
        page_url = urljoin(BASE_URL, f"/page/{page_num}")
        page = requests.get(page_url).content
        soup = BeautifulSoup(page, "html.parser")
        has_quote = soup.select_one(".quote")

        if has_quote is None:
            break

        all_quotes.extend(get_single_page_quote(soup))

    return all_quotes


def write_vacancies_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELD)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_home_quotes()
    write_vacancies_to_csv(quotes=quotes, output_csv_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
