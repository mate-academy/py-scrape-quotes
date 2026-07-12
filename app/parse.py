import csv
import logging
import sys
from dataclasses import asdict, dataclass
import requests
from bs4 import BeautifulSoup
from bs4.element import AttributeValueList


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)8s]: %(message)s",
    handlers=[
        logging.FileHandler("parser.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)


def fetch_html(url: str) -> str | None:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        logging.error(
            f"Server returned status {response.status_code} for URL: {url}"
        )
    except requests.RequestException as e:
        logging.error(f"Network error: {e}")

    return None


def parse_page_quotes(html_content: str) -> list[Quote] | None:
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")
    first_quote_div = soup.find_all("div", class_="quote")

    if not first_quote_div:
        return None

    quotes_list = []

    for quote_div in first_quote_div:
        quote_obj = Quote(
            text=quote_div.find("span", class_="text").text,
            author=quote_div.find("small", class_="author").text,
            tags=[tag.text for tag in quote_div.find_all("a", class_="tag")],
        )
        quotes_list.append(quote_obj)

    return quotes_list


def get_next_page_url(html_content: str) -> None | str | AttributeValueList:
    soup = BeautifulSoup(html_content, "html.parser")

    pagination = soup.select_one(".next a")
    if pagination is None:
        return None
    return pagination.get("href")


def save_to_csv(output_csv_path: str, data: list[Quote]) -> None:
    fieldnames = ["text", "author", "tags"]

    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for quote in data:
            row = asdict(quote)
            row["tags"] = str(row["tags"])
            writer.writerow(row)

    logging.info(f"Data successfully saved to {output_csv_path}")


def main(output_csv_path: str = "quotes.csv") -> None:
    base_url = "https://quotes.toscrape.com/"
    current_url = "https://quotes.toscrape.com"
    all_quotes = []

    logging.info("Start parsing quotes...")

    while base_url:
        logging.info(f"Parse page: {base_url}")

        html = fetch_html(base_url)
        if not html:
            logging.warning(f"Failed to load page: {base_url}")
            break

        quote_data = parse_page_quotes(html)
        if quote_data:
            all_quotes.extend(quote_data)

        pagination_url = get_next_page_url(html)

        if pagination_url:
            base_url = f"{current_url}{pagination_url}"
        else:
            base_url = None

    save_to_csv(output_csv_path, all_quotes)

    logging.info("Finished parsing quotes...")
    logging.info(f"Total collected quotes: {len(all_quotes)}")


if __name__ == "__main__":
    main()
