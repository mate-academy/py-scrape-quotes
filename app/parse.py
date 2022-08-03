import csv
from dataclasses import dataclass
from bs4 import BeautifulSoup

import requests


URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def take_author_biography(quote, author_name):
    link = quote.select_one("div.quote span a").attrs["href"]
    response = requests.get(URL + link).content
    soup = BeautifulSoup(response, "html.parser")

    author = author_name
    born = soup.select_one(".author-born-date").text
    description = soup.select_one(".author-description").text

    data = [author, born, description]

    return data


def create_csv_file(file_name: str, data: list, first_row):

    with open(file_name, "a", encoding='UTF8', newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(first_row)
        writer.writerows(data)


def take_data_from_quotes(quotes):
    data = []
    biography = []

    for quote in quotes:
        phrase = quote.select_one(".text").text
        author = quote.select_one(".author").text
        tag_list = [x.text for x in quote.select(".tag")]

        result = [phrase, author, tag_list]

        biography.append(take_author_biography(quote, author))
        print(biography)
        data.append(result)

    return [data, biography]


def main(output_csv_path: str) -> None:

    list_of_data = []
    biography = []
    counter = 1

    while True:

        responce = requests.get(f"{URL}/page/{counter}/").content
        soup = BeautifulSoup(responce, "html.parser")
        quotes = soup.select(".quote")

        if not quotes:
            break

        list_of_data += take_data_from_quotes(quotes)[0]
        biography += take_data_from_quotes(quotes)[1]

        counter += 1

    create_csv_file(
        output_csv_path,
        list_of_data,
        ["text", "author", "tags"]
    )
    create_csv_file(
        "biography.csv",
        biography,
        ["author", "born", "description"]
    )


if __name__ == "__main__":
    main("quotes.csv")
