from dataclasses import fields

from app.authors import Author
from app.quotes import get_quotes, Quote, AUTHORS_LIST
from app.utils import write_objects_to_csv


QUOTE_FIELDS = [quote_field.name for quote_field in fields(Quote)]
AUTHOR_FIELDS = [author_field.name for author_field in fields(Author)]


def main(quotes_csv_path: str, authors_csv_path: str = None) -> None:
    quotes = get_quotes()
    write_objects_to_csv(quotes, quotes_csv_path, QUOTE_FIELDS)
    if authors_csv_path:
        write_objects_to_csv(AUTHORS_LIST, authors_csv_path, AUTHOR_FIELDS)


if __name__ == "__main__":
    main("quotes.csv", "authors.csv")
