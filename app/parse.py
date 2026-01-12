from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import csv


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def main(output_csv_path: str) -> None:
    number = 1

    formatdict = []
    fields = ["text", "author", "tags"]

    while True:
        response = requests.get(f"https://quotes.toscrape.com/page/{number}/")

        soup = BeautifulSoup(response.text, "html.parser")

        infos = soup("div", {"class": "quote"})

        if not infos:
            break

        for info in infos:
            name = info.small.string
            text = info.span.string
            tags_str = info.meta.get("content")

            if tags_str:
                tags = tags_str.split(",")
            else:
                tags = []

            class_object = Quote(text, name, tags)

            formatdict.append(
                {
                    "text": class_object.text,
                    "author": class_object.author,
                    "tags": class_object.tags}
            )

        number += 1
    with open(output_csv_path, "w") as file:
        writer = csv.DictWriter(file, fieldnames=fields)

        writer.writeheader()

        writer.writerows(formatdict)


if __name__ == "__main__":
    main("quotes.csv")
