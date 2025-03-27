import csv
import dataclasses
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in dataclasses.fields(Quote)]


def get_all_quotes() -> list[Tag]:
    links = [BASE_URL + f"page/{i}/" for i in range(1, 11)]
    quotes_list = []
    for link in links:
        req = requests.get(link)
        soup = BeautifulSoup(req.content, "html.parser")
        quotes = soup.select("div.quote")
        quotes_list.extend(quotes)
    return quotes_list


def parse_quotes() -> list[Quote]:
    quotes = get_all_quotes()
    quotes_list = []
    for quote in quotes:
        text = quote.select_one("span.text").text
        author = quote.select_one("small.author").text
        tags = [tag.text for tag in quote.select("div.tags a")]

        quotes_list.append(Quote(text=text, author=author, tags=tags))

    return quotes_list


def write_quotes(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([dataclasses.astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes_list = parse_quotes()
    write_quotes(quotes_list, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
