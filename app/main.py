import csv
import logging
from dataclasses import astuple

from app.config import Quote, Author, URL, QUOTE_FIELDS, AUTHOR_FIELDS
from app.logger import configure_logger
from app.parser import parse_single_quote
from app.scrapper import scrape_all_raw_quotes, scrape_and_parse_all_authors

configure_logger()


def write_to_csv(
        data: list[Quote | Author],
        fieldnames: list[str],
        output_csv_path: str
) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as csvfile:
        logging.info(f"Writing to {output_csv_path}")

        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)
        writer.writerows([astuple(entry) for entry in data])


def main(output_csv_quotes_path: str, output_csv_authors_path: str) -> None:
    raw_quotes = scrape_all_raw_quotes(URL)

    quotes = [parse_single_quote(quote) for quote in raw_quotes]
    authors = scrape_and_parse_all_authors(raw_quotes)

    write_to_csv(quotes, QUOTE_FIELDS, output_csv_quotes_path)
    write_to_csv(authors, AUTHOR_FIELDS, output_csv_authors_path)


if __name__ == "__main__":
    main("quotes.csv", "authors.csv")
