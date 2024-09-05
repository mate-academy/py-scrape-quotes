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
    description: str


def get_author_bio(author_link: str) -> str:
    author_page = requests.get(BASE_URL + author_link)
    author_soup = bs4.BeautifulSoup(author_page.text, 'html.parser')
    return author_soup.select_one(".author-description").text.strip()


def quotes_from_one_page(soup: bs4.BeautifulSoup) -> list[Quote]:
    result_list = []
    authors_cached = {}
    all_quotes = soup.select(".quote")
    for quote in all_quotes:
        author_link = quote.select_one("span > a")["href"]
        author = quote.select_one(".author").text
        if author in authors_cached:
            description = authors_cached[author]
        else:
            description = get_author_bio(author_link)
            authors_cached[author] = description
        result_list.append(Quote(
            text=quote.select_one(".text").text,
            author=author,
            tags=[tag.text for tag in quote.select(".tags > .tag")],
            description=description
        )
        )

    return result_list


def write_products_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        write = csv.writer(file)
        write.writerow(["text", "author", "tags", "description"])
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
