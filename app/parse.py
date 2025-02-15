import csv
from dataclasses import dataclass, fields, astuple
from bs4 import BeautifulSoup, Tag
import requests

SITE_URL = "https://quotes.toscrape.com"
PARAMS = {"page": 1}


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_quote(quote_tag: Tag) -> Quote:
    return Quote(
        text=quote_tag.select_one(".text").text,
        author=quote_tag.select_one(".author").text,
        tags=[tag.text for tag in quote_tag.select(".tag")]
    )


def get_html_from_url(url: str) -> [Quote]:
    all_quotes = []
    while True:

        current_page = f"{url}/page/{PARAMS['page']}"
        print(f"Parsing {current_page}")
        page_html = requests.get(current_page).content
        page_soup = BeautifulSoup(page_html, "html.parser")

        quotes = page_soup.select(".quote")
        all_quotes.extend([parse_quote(qoute) for qoute in quotes])
        pagination = page_soup.select_one(".pager")
        if not pagination.select_one(".next"):
            print(f"Finished parsing at {current_page},"
                  f" total quotes: {len(all_quotes)}")

            break
        else:
            PARAMS["page"] += 1

    return all_quotes


def write_qoutes_to_csv(quotes: [Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(qoute) for qoute in quotes])


def main(output_csv_path: str) -> None:
    write_qoutes_to_csv(get_html_from_url(SITE_URL), output_csv_path)
    print("Done!")
    print("Check out the result in {}".format(output_csv_path))


if __name__ == "__main__":
    main("quotes.csv")
