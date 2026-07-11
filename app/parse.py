import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


quotes_site_url = "https://quotes.toscrape.com/"
quotes_fields = [field.name for field in fields(Quote)]


def get_num_pages() -> int:
    pages_count = 1
    while True:
        page_soup = parse_page(quotes_site_url + f"/page/{pages_count}/")
        pagination = page_soup.select_one("li.next")
        if pagination:
            pages_count += 1
        else:
            break
    return pages_count


def parse_page(url_page: str) -> BeautifulSoup:
    response = requests.get(url_page)
    response.raise_for_status()
    page_soup = BeautifulSoup(response.content, "html.parser")
    return page_soup


def quotes_objects_in_one_page(page_soup: BeautifulSoup) -> list[Quote]:
    quotes = page_soup.select(".quote")
    quotes_objects = []
    for quote in quotes:
        quote_object = Quote(
            text=quote.select_one("span.text").text,
            author=quote.select_one("small.author").text,
            tags=[tag.get_text(strip=True) for tag in quote.select(".tag")])
        quotes_objects.append(quote_object)
    return quotes_objects


def parse_all_pages() -> list[list[Quote]]:
    num_of_pages = get_num_pages()
    elements = []
    for page in range(1, num_of_pages + 1):
        page_soup = parse_page(quotes_site_url + f"/page/{page}/")
        quotes = quotes_objects_in_one_page(page_soup=page_soup)
        elements.append(quotes)
    return elements


def write_quotes_list_to_csv_file(
        output_csv_path: str,
        all_quotes: list[list[Quote]]
) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        csv_file = csv.writer(file)
        csv_file.writerow(quotes_fields)
        for quotes_list in all_quotes:
            csv_file.writerows([astuple(quote) for quote in quotes_list])


def main(output_csv_path: str) -> None:
    all_quotes = parse_all_pages()
    write_quotes_list_to_csv_file(all_quotes=all_quotes,
                                  output_csv_path=output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
