import csv
from dataclasses import astuple, dataclass
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from selenium import webdriver

BASE_URL = "https://quotes.toscrape.com/"


class WebDriver:
    def __enter__(self) -> object:
        self.driver = webdriver.Chrome()
        return self.driver

    def __exit__(
            self,
            exc_type: object,
            exc_value: object,
            traceback: object
    ) -> None:
        self.driver.quit()


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quote(quote_soup: BeautifulSoup) -> Quote:
    return Quote(
        text=quote_soup.select_one(".text").text,
        author=quote_soup.select_one(".author").text,
        tags=[tag.text for tag in quote_soup.select(".tag")]
    )


def get_quotes_per_page(
        num_page: int,
        driver: webdriver.Chrome
) -> list[Quote]:
    url = urljoin(BASE_URL, f"page/{num_page}/")
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    quotes = soup.select(".quote")
    return [get_single_quote(quote_soup) for quote_soup in quotes]


def get_quotes() -> list[Quote]:
    with WebDriver() as driver:
        num_page = 1
        all_quotes = []
        while True:
            quotes = get_quotes_per_page(num_page, driver)
            if not quotes:
                break
            all_quotes.extend(quotes)
            num_page += 1
        return all_quotes


def write_quotes_to_csv(output_csv_path: str, quotes: list[Quote]) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("text", "author", "tags"))
        for quote in quotes:
            writer.writerow(astuple(quote))


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
