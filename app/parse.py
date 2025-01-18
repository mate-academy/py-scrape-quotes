import csv
import dataclasses
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup, Tag, ResultSet

HOME_PAGE_URL = "https://quotes.toscrape.com"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quote(single_quote: Tag) -> Quote:
    try:
        text = single_quote.find_all("span", class_="text")[0].text
    except IndexError:
        raise IndexError("Error extracting 'text': No element with class 'text' found in the provided tag.")

    try:
        author = single_quote.find_all("small", class_="author")[0].text
    except IndexError:
        raise IndexError("Error extracting 'author': No element with class 'author' found in the provided tag.")

    tags = [elem.text for elem in single_quote.find_all("a", class_="tag")]

    return Quote(text=text, author=author, tags=tags)


def page_with_quotes(soup_page: BeautifulSoup) -> ResultSet:
    block_quote = soup_page.select(".quote")
    return block_quote


def next_page(page: BeautifulSoup) -> str | None:
    page = page.find("li", class_="next")
    if page:
        tag_a = page.find("a")
        if tag_a and "href" in tag_a.attrs:
            return HOME_PAGE_URL + tag_a.get("href")
    return None


def main(output_csv_path: str) -> None:
    all_quotes = []
    url = HOME_PAGE_URL
    while url:
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise requests.exceptions.HTTPError(f"HTTP request failed. Status code: {response.status_code} ")
            response = response.content
            soup = BeautifulSoup(response, "html.parser")

            if page_with_quotes(soup):
                block_quote = page_with_quotes(soup)
                parsed_quotes = [get_single_quote(info)
                                 for info in block_quote]
                all_quotes.extend(quotes.__dict__ for quotes in parsed_quotes)
            url = next_page(soup)
        except requests.RequestException as e:
            print(f"When parse got error {e}")
            break

    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [attr.name for attr in dataclasses.fields(Quote)]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        writer.writerows(all_quotes)


if __name__ == "__main__":
    main("quotes.csv")
