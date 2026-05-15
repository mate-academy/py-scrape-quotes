import csv
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag, ResultSet

import requests


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


quotes_url = "https://quotes.toscrape.com/page/"

quote_fields = [field.name for field in fields(Quote)]


def creation_quote_model(
        author_quote: str,
        text_quote: str,
        tag_list: list[str]
) -> Quote:
    quote_model = Quote(
        text=text_quote,
        author=author_quote,
        tags=tag_list
    )
    return quote_model


def parsing_tags_in_quote(tags_quote_list: ResultSet[Tag]) -> list:
    return [tag_quote.text for tag_quote in tags_quote_list]


def writing_csv_file(output_csv_path: str, quotes_model: [Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(quote_fields)
        writer.writerows([astuple(quote) for quote in quotes_model])


def parsing_quotes_on_page(all_quotes_on_page_soup: ResultSet[Tag]) -> list:
    result_on_page = []
    for quote in all_quotes_on_page_soup:
        author_quote = quote.select_one(".author").text
        text_quote = quote.select_one(".text").text
        tags_quote_list = quote.select(".tag")
        tag_list = parsing_tags_in_quote(tags_quote_list)
        quote_model = creation_quote_model(
            author_quote=author_quote,
            text_quote=text_quote,
            tag_list=tag_list
        )
        result_on_page.append(quote_model)
    return result_on_page


def parsing_all_quotes() -> list:
    result = []
    page = 1
    while True:
        response = requests.get(
            f"{quotes_url}{page}/"
        ).content
        soup = BeautifulSoup(response, "html.parser")
        all_quotes_on_page_soup = soup.select(".quote")
        if len(all_quotes_on_page_soup) == 0:
            print("Writing completed")
            break
        parsing_on_page_result = (
            parsing_quotes_on_page(all_quotes_on_page_soup)
        )
        result.extend(parsing_on_page_result)
        page += 1
    return result


def main(output_csv_path: str) -> None:
    quotes = parsing_all_quotes()
    writing_csv_file(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
