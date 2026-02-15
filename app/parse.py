from dataclasses import dataclass
import csv
import html
import time
from html.parser import HTMLParser
from typing import Iterable
from urllib.parse import urljoin
from urllib.request import Request, urlopen


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def _iter_all_quotes(start_url: str) -> Iterable[Quote]:
    url: str | None = start_url

    while url is not None:
        page_html = _fetch_html(url)
        quotes, next_href = _parse_quotes_page(page_html)
        yield from quotes

        url = urljoin(url, next_href) if next_href else None

        if url is not None:
            time.sleep(0.1)


def _fetch_html(url: str, *, timeout: float = 15.0) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; QuoteScraper/1.0)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _parse_quotes_page(page_html: str) -> tuple[list[Quote], str | None]:
    parser = _QuotesHTMLParser()
    parser.feed(page_html)
    parser.close()

    return parser.quotes, parser.next_href


def _has_class(attrs: dict[str, str], class_name: str) -> bool:
    classes = attrs.get("class", "").split()

    return class_name in classes


class _QuotesHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.quotes: list[Quote] = []
        self.next_href: str | None = None

        self._in_quote = False
        self._quote_div_depth = 0
        self._current_text: str | None = None
        self._current_author: str | None = None
        self._current_tags: list[str] = []

        self._capture: str | None = None
        self._buffer: list[str] = []

        self._in_next_li = False

    def handle_starttag(
        self, tag: str, attrs_list: list[tuple[str, str | None]]
    ) -> None:
        attrs: dict[str, str] = {
            key: value for key, value in attrs_list if value is not None
        }

        if tag == "li" and _has_class(attrs, "next"):
            self._in_next_li = True

        if self._in_next_li and tag == "a" and "href" in attrs:
            self.next_href = attrs["href"]

        if tag == "div" and _has_class(attrs, "quote"):
            self._in_quote = True
            self._quote_div_depth = 1
            self._current_text = None
            self._current_author = None
            self._current_tags = []

            return

        if self._in_quote and tag == "div":
            self._quote_div_depth += 1

        if self._in_quote and tag == "span" and _has_class(attrs, "text"):
            self._start_capture("text")

            return

        if self._in_quote and tag == "small" and _has_class(attrs, "author"):
            self._start_capture("author")

            return

        if self._in_quote and tag == "a" and _has_class(attrs, "tag"):
            self._start_capture("tag")

    def handle_endtag(self, tag: str) -> None:
        if self._capture == "text" and tag == "span":
            self._current_text = self._finish_capture()

            return

        if self._capture == "author" and tag == "small":
            self._current_author = self._finish_capture()

            return

        if self._capture == "tag" and tag == "a":
            tag_text = self._finish_capture().strip()
            if tag_text:
                self._current_tags.append(tag_text)

            return

        if self._in_next_li and tag == "li":
            self._in_next_li = False

        if self._in_quote and tag == "div":
            self._quote_div_depth -= 1
            if self._quote_div_depth == 0:
                self._in_quote = False
                self._finalize_quote()

    def handle_data(self, data: str) -> None:
        if self._capture is not None:
            self._buffer.append(data)

    def _start_capture(self, kind: str) -> None:
        self._capture = kind
        self._buffer = []

    def _finish_capture(self) -> str:
        data = "".join(self._buffer)
        self._capture = None
        self._buffer = []

        return html.unescape(data).strip()

    def _finalize_quote(self) -> None:
        if self._current_text is None or self._current_author is None:
            return

        self.quotes.append(
            Quote(
                text=self._current_text,
                author=self._current_author,
                tags=self._current_tags,
            )
        )


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com/"

    with open(output_csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in _iter_all_quotes(base_url):
            writer.writerow([quote.text, quote.author, str(quote.tags)])


if __name__ == "__main__":
    main("quotes.csv")
