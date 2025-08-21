import csv
from dataclasses import astuple
from typing import Callable, Optional

import requests
from bs4 import Tag, BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


def get_first_page_soup() -> Optional[BeautifulSoup]:
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error {e}")


def is_next_page(soup: Tag) -> bool:
    next_page = soup.select(".next")
    if not next_page:
        return False
    return True


def write_elements_to_csv(elements: list, path: str, fields: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(fields)
        for element in elements:
            row = list(astuple(element))

            if row and isinstance(row[-1], list):
                row[-1] = ",".join(row[-1]) if row[-1] else ""

            writer.writerow(row)


def get_all_items(parse_func: Callable[[BeautifulSoup], list]) -> list:
    first_page_soup = get_first_page_soup()
    items = parse_func(first_page_soup)

    i = 1
    while True:
        i += 1
        try:
            response = requests.get(f"{BASE_URL}page/{i}")
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error {e}")
            continue
        next_page_soup = BeautifulSoup(response.content, "html.parser")
        items.extend(parse_func(next_page_soup))
        if not is_next_page(next_page_soup):
            break
    return items
