import csv
from dataclasses import dataclass, astuple, fields
import requests
from bs4 import BeautifulSoup, Tag

URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELD = [field.name for field in fields(Quote)]


def create_quote_object(soup: Tag) -> Quote:
    return Quote(
        text=soup.select_one(".text").text,
        author=soup.select_one(".author").text,
        tags=[tag.text for tag in soup.select(".tags > a")]
    )


def get_single_data(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    return [create_quote_object(page) for page in quotes]


def get_data() -> list[Quote]:
    next_url_to_scrape = URL
    all_quotes = []

    while next_url_to_scrape:
        page = requests.get(next_url_to_scrape).content
        soup = BeautifulSoup(page, "html.parser")
        all_quotes.extend(get_single_data(soup))

        next_button = soup.find(class_="next")
        if next_button is None:
            break

        next_url_to_scrape = URL + next_button.find("a")["href"]

    return all_quotes


def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELD)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    data = get_data()
    write_quotes_to_csv(data, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
