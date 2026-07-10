from dataclasses import dataclass
import csv
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import urlopen


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


class QuotesParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.quotes: list[Quote] = []
        self.next_page_url: str | None = None
        self._current_text = ""
        self._current_author = ""
        self._current_tags: list[str] = []
        self._is_quote = False
        self._is_text = False
        self._is_author = False
        self._is_tag = False
        self._is_next = False

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attrs_dict = dict(attrs)
        classes = attrs_dict.get("class", "").split()

        if tag == "div" and "quote" in classes:
            self._is_quote = True
            self._current_text = ""
            self._current_author = ""
            self._current_tags = []
        elif self._is_quote and tag == "span" and "text" in classes:
            self._is_text = True
        elif self._is_quote and tag == "small" and "author" in classes:
            self._is_author = True
        elif self._is_quote and tag == "a" and "tag" in classes:
            self._is_tag = True
        elif tag == "li" and "next" in classes:
            self._is_next = True
        elif self._is_next and tag == "a":
            href = attrs_dict.get("href")
            if href is not None:
                self.next_page_url = urljoin(BASE_URL, href)

    def handle_endtag(self, tag: str) -> None:
        if tag == "div" and self._is_quote:
            self.quotes.append(
                Quote(
                    text=self._current_text,
                    author=self._current_author,
                    tags=self._current_tags,
                )
            )
            self._is_quote = False
        elif tag == "span":
            self._is_text = False
        elif tag == "small":
            self._is_author = False
        elif tag == "a":
            self._is_tag = False
        elif tag == "li":
            self._is_next = False

    def handle_data(self, data: str) -> None:
        if self._is_text:
            self._current_text += data
        elif self._is_author:
            self._current_author += data
        elif self._is_tag:
            self._current_tags.append(data)


def get_page_html(url: str) -> str:
    with urlopen(url) as response:
        return response.read().decode("utf-8")


def parse_quotes_page(url: str) -> tuple[list[Quote], str | None]:
    parser = QuotesParser()
    parser.feed(get_page_html(url))
    return parser.quotes, parser.next_page_url


def get_all_quotes() -> list[Quote]:
    quotes: list[Quote] = []
    next_page_url: str | None = BASE_URL

    while next_page_url is not None:
        page_quotes, next_page_url = parse_quotes_page(next_page_url)
        quotes.extend(page_quotes)

    return quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        writer.writerows(
            [quote.text, quote.author, quote.tags]
            for quote in get_all_quotes()
        )


if __name__ == "__main__":
    main("quotes.csv")
