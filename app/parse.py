import requests
import csv
from bs4 import BeautifulSoup
from dataclasses import dataclass


URL = "https://quotes.toscrape.com/page/{page_number}/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        counter = 1
        while counter < 11:
            response = requests.get(URL.format(page_number=counter))

            soup = BeautifulSoup(response.content, "html.parser")

            quotes = soup.select("div.quote span.text")
            authors = soup.select("div.quote span small.author")
            tags = soup.select("div.quote div.tags meta")

            lst = []
            for i in range(len(quotes)):
                lst.append(
                    Quote(
                        text=quotes[i].text,
                        author=authors[i].text,
                        tags=tags[i].get(
                            "content"
                        ).split(",") if tags[i].get(
                            "content"
                        ) != "" else []
                    )
                )
            counter += 1
            for quote in lst:
                writer.writerow(quote.__dict__.values())


if __name__ == "__main__":
    main("quotes.csv")
