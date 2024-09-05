import csv

import requests
import bs4
from dataclasses import dataclass, astuple

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def quotes_from_one_page(soup: bs4.BeautifulSoup) -> list[Quote]:
    result_list = []
    all_quotes = soup.select(".quote")
    for quote in all_quotes:
        result_list.append(Quote(
            text=quote.select_one(".text").text,
            author=quote.select_one(".author").text,
            tags=[tag.text for tag in quote.select(".tags > .tag")],
        )
        )

    return result_list


def write_products_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        write = csv.writer(file)
        write.writerow(["text", "author", "tags"])
        write.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    all_quotes = []
    page_counter = 1
    while True:
        page = requests.get(BASE_URL + f"page/{page_counter}/")
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        if " ".join(
                soup.select(".col-md-8")[1].text.strip().split()[:3]
        ) == "No quotes found!":
            break
        all_quotes.extend(quotes_from_one_page(soup))

        page_counter += 1

    write_products_to_csv(all_quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
