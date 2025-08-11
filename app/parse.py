import ast
import csv
import json
from typing import Optional, List
from bs4 import BeautifulSoup
from pydantic import BaseModel, field_validator
import requests
from time import sleep

BASE_URL = "https://quotes.toscrape.com"


class Quote(BaseModel):
    text: str
    author: str
    tags: List[str]
    author_link: Optional[str] = None

    def __init__(self, *args: object, **kwargs: object) -> None:
        if args and not kwargs:
            field_names = list(self.__class__.model_fields.keys())
            kwargs = {field_names[i]: arg for i, arg in enumerate(args)}
        super().__init__(**kwargs)

    @field_validator("tags", mode="before")
    @classmethod
    def parse_tags(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            try:
                return ast.literal_eval(value)
            except Exception:
                return [tag.strip() for tag in value.split(",")]
        return value


class QuoteParser:
    def __init__(self, html: str) -> None:
        self.soup = BeautifulSoup(html, "html.parser")

    def parse(self) -> List[Quote]:
        quotes = []
        quote_blocks = self.soup.select("div.quote")
        for block in quote_blocks:
            text = block.select_one("span.text").get_text(strip=True)
            author = block.select_one("small.author").get_text(strip=True)
            author_link = BASE_URL + block.select_one("span a")["href"]
            tags = [
                tag.get_text(strip=True)
                for tag in block.select("div.tags a.tag")
            ]
            quotes.append(Quote(text, author, tags, author_link))
        return quotes


class QuoteCSVWriter:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

    def write(self, quotes: List[Quote]) -> None:
        with open(
                self.file_path, mode="w",
                newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["text", "author", "tags", "author_link"])
            for quote in quotes:
                writer.writerow([
                    quote.text,
                    quote.author,
                    json.dumps(quote.tags, ensure_ascii=False),
                    quote.author_link or "",
                ])


def main(output_csv_path: str) -> None:
    url = BASE_URL
    all_quotes: List[Quote] = []

    while url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            html = response.text
        except requests.RequestException as e:
            print(f"Ошибка запроса {url}: {e}. Пропускаем страницу.")
            break

        parser = QuoteParser(html)
        quotes = parser.parse()
        all_quotes.extend(quotes)

        soup = BeautifulSoup(html, "html.parser")
        next_button = soup.select_one("li.next > a")
        url = BASE_URL + next_button["href"] if next_button else None

        sleep(1)

    csv_writer = QuoteCSVWriter(output_csv_path)
    csv_writer.write(all_quotes)


if __name__ == "__main__":
    main("quotes.csv")
