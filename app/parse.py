import csv
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen

BASE_URL = "https://quotes.toscrape.com/"
REQUEST_DELAY = 0.2


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


class QuotesParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.quotes: list[Quote] = []
        self.next_page: str | None = None

        self._inside_quote = False
        self._quote_div_depth = 0

        self._text = ""
        self._author = ""
        self._tags: list[str] = []

        self._capture_text = False
        self._capture_author = False
        self._capture_tag = False
        self._tag_text = ""

        self._inside_next_li = False

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attrs_dict = dict(attrs)
        classes = (attrs_dict.get("class") or "").split()

        if tag == "div" and "quote" in classes:
            self._inside_quote = True
            self._quote_div_depth = 1

            self._text = ""
            self._author = ""
            self._tags = []
            return

        if self._inside_quote and tag == "div":
            self._quote_div_depth += 1

        if (
            self._inside_quote
            and tag == "span"
            and "text" in classes
        ):
            self._capture_text = True

        elif (
            self._inside_quote
            and tag == "small"
            and "author" in classes
        ):
            self._capture_author = True

        elif (
            self._inside_quote
            and tag == "a"
            and "tag" in classes
        ):
            self._capture_tag = True
            self._tag_text = ""

        if tag == "li" and "next" in classes:
            self._inside_next_li = True

        elif self._inside_next_li and tag == "a":
            self.next_page = attrs_dict.get("href")

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self._capture_text:
            self._capture_text = False

        elif tag == "small" and self._capture_author:
            self._capture_author = False

        elif tag == "a" and self._capture_tag:
            self._capture_tag = False
            self._tags.append(self._tag_text.strip())

        elif tag == "li" and self._inside_next_li:
            self._inside_next_li = False

        if self._inside_quote and tag == "div":
            self._quote_div_depth -= 1

            if self._quote_div_depth == 0:
                self.quotes.append(
                    Quote(
                        text=self._text.strip(),
                        author=self._author.strip(),
                        tags=self._tags.copy(),
                    )
                )

                self._inside_quote = False

    def handle_data(self, data: str) -> None:
        if self._capture_text:
            self._text += data

        elif self._capture_author:
            self._author += data

        elif self._capture_tag:
            self._tag_text += data


def fetch_html(url: str) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
    )

    with urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8")


def parse_page(
    html: str,
) -> tuple[list[Quote], str | None]:
    parser = QuotesParser()
    parser.feed(html)

    return parser.quotes, parser.next_page


def get_all_quotes() -> list[Quote]:
    quotes: list[Quote] = []
    url: str | None = BASE_URL

    while url is not None:
        html = fetch_html(url)

        page_quotes, next_page = parse_page(html)

        quotes.extend(page_quotes)

        if next_page:
            url = urljoin(url, next_page)
        else:
            url = None

        if url is not None:
            time.sleep(REQUEST_DELAY)

    return quotes


def write_quotes_to_csv(
    quotes: list[Quote],
    output_csv_path: str,
) -> None:
    with open(
        output_csv_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "text",
                "author",
                "tags",
            ]
        )

        for quote in quotes:
            writer.writerow(
                [
                    quote.text,
                    quote.author,
                    quote.tags,
                ]
            )


def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(
        quotes,
        output_csv_path,
    )


if __name__ == "__main__":
    main("quotes.csv")
