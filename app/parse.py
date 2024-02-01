import csv
from dataclasses import dataclass, fields, astuple
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://quotes.toscrape.com/page/{num_page}/'

OUTPUT_CSV_PATH = 'quotes.csv'


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


@dataclass
class AuthorsBiography:
    name: str
    biography: str


AUTHORS_BIOGRAPHY_FIELDS = [field.name for field in fields(AuthorsBiography)]


def parse_single_quotes(quoter_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quoter_soup.select_one('span.text[itemprop="text"]').get_text(strip=True),
        author=quoter_soup.select_one('span > small').get_text(strip=True),
        tags=[tag.get_text(strip=True) for tag in quoter_soup.find_all('a', class_='tag')]
    )


def parse_single_authors_biography(authors_soup: BeautifulSoup) -> AuthorsBiography:
    return AuthorsBiography(
        name=authors_soup.select_one(".author-title").get_text(strip=True),
        biography=authors_soup.select_one('.author-description').get_text(strip=True)
    )


def get_quotes_some_page(num_page: int) -> list[Quote]:
    url = BASE_URL.format(num_page=num_page)
    response = requests.get(url)
    print(response.text)
    if response.status_code == 200:
        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        quotes = soup.find_all("div", class_="quote")
        return [parse_single_quotes(quoter_soup) for quoter_soup in quotes]

    else:
        print(f"Request failed with status code {response.status_code}")


def get_quotes_all_pages() -> list[Quote]:
    num_page = 1
    all_quotes = []
    while True:
        quotes_on_page = get_quotes_some_page(num_page)

        if not quotes_on_page:
            break  # No more pages

        all_quotes.extend(quotes_on_page)
        num_page += 1

    return all_quotes


def write_csv(quotes: [Quote]) -> None:
    with open(OUTPUT_CSV_PATH, 'w', newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes_all_pages()
    write_csv(quotes)


if __name__ == "__main__":
    main("quotes.csv")
