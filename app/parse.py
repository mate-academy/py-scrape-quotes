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

    def make_request(self):
        if self.PARAMS:
            r = requests.get(self.HOME_PAGE + self.PARAMS)
        else:
            r = requests.get(self.HOME_PAGE)
        self.SOUP = BeautifulSoup(r.text, 'html.parser')

    def parse_page(self):
        for el in self.SOUP.find_all(class_="quote"):
            self.RESULT_TABLE.append(Quote(
                text=el.find(itemprop="text").text,
                author=el.find(itemprop="author").text,
                tags=[] if el.find(itemprop="keywords")['content'].split(',') == [''] else el.find(itemprop="keywords")['content'].split(',')
                  ))

        if self.SOUP.find(class_="next"):
            self.PARAMS = str(self.SOUP.find(class_="next").a['href'])
            self.DO_PAGINATION = True
        else:
            self.DO_PAGINATION = False

    def fill_table(self, output_csv_path):
        with open(output_csv_path, "w") as stream:
            writer = csv.writer(stream)
            writer.writerow(['text', 'author', 'tags'])
            for row in self.RESULT_TABLE:
                print(row.tags)
                writer.writerow([row.text, row.author, row.tags])


def main(output_csv_path: str) -> None:
    pr = Parse()
    while pr.DO_PAGINATION:
        pr.make_request()
        pr.parse_page()
    pr.fill_table(output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")

