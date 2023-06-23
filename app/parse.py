import csv
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class Parse:
    HOME_PAGE = "https://quotes.toscrape.com/"
    RESULT_TABLE = []
    PARAMS = ""
    SOUP = ""
    DO_PAGINATION = True

    def make_request(self) -> None:
        if self.PARAMS:
            re = requests.get(self.HOME_PAGE + self.PARAMS)
        else:
            re = requests.get(self.HOME_PAGE)
        self.SOUP = BeautifulSoup(re.text, "html.parser")

    def parse_page(self) -> None:
        for el in self.SOUP.find_all(class_="quote"):
            list_of_cont = el.find(itemprop="keywords")["content"].split(",")
            self.RESULT_TABLE.append(
                Quote(
                    text=el.find(itemprop="text").text,
                    author=el.find(itemprop="author").text,
                    tags=[] if list_of_cont == [""]
                    else list_of_cont,
                )
            )

        if self.SOUP.find(class_="next"):
            self.PARAMS = str(self.SOUP.find(class_="next").a["href"])
            self.DO_PAGINATION = True
        else:
            self.DO_PAGINATION = False

    def fill_table(self, output_csv_path: str) -> None:
        with open(output_csv_path, "w") as stream:
            writer = csv.writer(stream)
            writer.writerow(["text", "author", "tags"])
            for row in self.RESULT_TABLE:
                writer.writerow([row.text, row.author, row.tags])


def main(output_csv_path: str) -> None:
    pr = Parse()
    while pr.DO_PAGINATION:
        pr.make_request()
        pr.parse_page()
    pr.fill_table(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
