from __future__ import annotations

import csv
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.request import Request, urlopen


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


class QuotePageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.quotes: list[Quote] = []
        self.next_page: str | None = None
        self._quote_depth = 0
        self._text_parts: list[str] = []
        self._author_parts: list[str] = []
        self._tags: list[str] = []
        self._capture_text = False
        self._capture_author = False
        self._capture_tag = False
        self._inside_next = False

    def handle_starttag(
            self,
            tag: str,
            attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        classes = attributes.get("class", "") or ""

        if tag == "div" and "quote" in classes.split():
            self._quote_depth = 1
            self._text_parts = []
            self._author_parts = []
            self._tags = []
        elif tag == "div" and self._quote_depth:
            self._quote_depth += 1

        if self._quote_depth:
            if tag == "span" and "text" in classes.split():
                self._capture_text = True
            elif tag == "small" and "author" in classes.split():
                self._capture_author = True
            elif tag == "a" and "tag" in classes.split():
                self._capture_tag = True

        if tag == "li" and "next" in classes.split():
            self._inside_next = True
        elif tag == "a" and self._inside_next:
            self.next_page = attributes.get("href")

    def handle_endtag(self, tag: str) -> None:
        if tag == "span":
            self._capture_text = False
        elif tag == "small":
            self._capture_author = False
        elif tag == "a":
            self._capture_tag = False
        elif tag == "li":
            self._inside_next = False

        if tag == "div" and self._quote_depth:
            self._quote_depth -= 1
            if not self._quote_depth:
                self.quotes.append(
                    Quote(
                        text="".join(self._text_parts).strip(),
                        author="".join(self._author_parts).strip(),
                        tags=self._tags.copy()
                    )
                )

    def handle_data(self, data: str) -> None:
        if self._capture_text:
            self._text_parts.append(data)
        elif self._capture_author:
            self._author_parts.append(data)
        elif self._capture_tag:
            self._tags.append(data.strip())


def fetch_page(url: str) -> str:
    request = Request(url, headers={"User-Agent": "quote-scraper/1.0"})
    with urlopen(request, timeout=10) as response:
        encoding = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(encoding)


def scrape_quotes(start_url: str = BASE_URL) -> list[Quote]:
    quotes: list[Quote] = []
    page_url: str | None = start_url

    while page_url:
        parser = QuotePageParser()
        parser.feed(fetch_page(page_url))
        quotes.extend(parser.quotes)
        page_url = (
            urljoin(page_url, parser.next_page)
            if parser.next_page
            else None
        )

    return quotes


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(("text", "author", "tags"))
        for quote in scrape_quotes():
            writer.writerow((quote.text, quote.author, quote.tags))


if __name__ == "__main__":
    main("quotes.csv")
