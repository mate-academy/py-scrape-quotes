import requests
import csv
from dataclasses import dataclass
from bs4 import BeautifulSoup


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_quotes() -> list[Quote]:
    qoutes = []

    url = "http://quotes.toscrape.com/"
    page = requests.get(url)
    while True:
        soup = BeautifulSoup(page.content, "html.parser")
        quote_elements = soup.find_all("div", class_="quote")
        for quote_element in quote_elements:
            text = quote_element.find("span", class_="text").get_text()
            author = quote_element.find("small", class_="author").get_text()
            tags = [
                tag.get_text()
                for tag in quote_element.find_all("a", class_="tag")
            ]
            qoutes.append(Quote(text, author, tags))

        next_button = soup.find("li", class_="next")
        if next_button is None:
            break

        next_page_url = next_button.find("a")["href"]
        page = requests.get(url + next_page_url)

    return qoutes


def main(output_csv_path: str) -> None:
    qoutes = get_quotes()
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])
        for quote in qoutes:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
