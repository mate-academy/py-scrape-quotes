from dataclasses import dataclass
from urllib.parse import urljoin

import requests as requests

from bs4 import BeautifulSoup

SITE = "https://quotes.toscrape.com/page/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_info(soup):
    text = soup.select_one(".text").text
    author = soup.select_one(".author").text
    tags = [
        tag.text for tag in
        soup.select(".tag")
    ]
    info = {
        "text": text,
        "author": author,
        "tags": tags
    }
    QCl = Quote(**info)
    return f"{QCl.text},{QCl.author},{QCl.tags}"


def parse_site(site_page_number):
    content = requests.get(urljoin(SITE, site_page_number)).content
    soup = BeautifulSoup(content, 'html.parser')

    quotes = soup.select('.quote')

    return [get_info(q) for q in quotes]


def check_pagination(url: str):
    content = requests.get(url).content
    soup = BeautifulSoup(content, "html.parser")

    return soup.select(".next")


def main(output_csv_path: str) -> None:
    with open(output_csv_path, 'w', encoding='utf-8') as f:
        start_page = 1
        info = parse_site(str(start_page))
        for line in info:
            f.writelines(f"{line}\n")
        while check_pagination(urljoin(SITE, str(start_page))):
            start_page += 1
            info = parse_site(str(start_page))
            for line in info:
                f.writelines(f"{line}\n")


if __name__ == "__main__":
    main("quotes.csv")
