from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import csv

BASE_URL = "https://quotes.toscrape.com/"
LIST_OF_QUOTES = []
AUTHORS_DESCRIPTION = {}


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

def get_single_quote(quote: BeautifulSoup) -> Quote:
    text = quote.select_one(".text").text
    author = quote.select_one(".author").text
    tags = [tag.text for tag in quote.select(".tag")]

    # get authors about
    if author not in AUTHORS_DESCRIPTION:
        a_tag = quote.select_one('span a[href]')
        link_about = a_tag.get('href')
        page_about = requests.get(BASE_URL + link_about)
        soup_about = BeautifulSoup(page_about.content, "html.parser")
        get_author_description(author, soup_about)

    return Quote(text, author, tags)


def get_author_description(author: str, soup_about: BeautifulSoup) -> None:
    description = soup_about.select_one(".author-description").text
    AUTHORS_DESCRIPTION[author] = description
    born = soup_about.select_one(".author-born-date").text
    born_place = soup_about.select_one(".author-born-location").text
    AUTHORS_DESCRIPTION[author] += f" (Born: {born} in {born_place})"


def scrap_pages(next_page: str = "") -> list[Quote]:
    page = requests.get(BASE_URL + next_page)
    soup = BeautifulSoup(page.content, "html.parser")
    quotes = soup.select(".quote")
    LIST_OF_QUOTES.extend([get_single_quote(quote) for quote in quotes])

    try:
        next_page = soup.select_one(".next a")['href']
    except TypeError:
        next_page = ""

    if next_page:
        scrap_pages(next_page)

    return LIST_OF_QUOTES


def main(output_csv_path: str) -> None:
    quotes = scrap_pages()

    with open(output_csv_path, "w", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['author', 'tags', 'text'])
        for quote in quotes:
            writer.writerow([quote.author, ', '.join(quote.tags), quote.text])

    with open("authors.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for author in AUTHORS_DESCRIPTION:
            writer.writerow([author, AUTHORS_DESCRIPTION[author]])


if __name__ == "__main__":
    main("quotes.csv")
