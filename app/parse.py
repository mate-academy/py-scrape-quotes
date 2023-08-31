from dataclasses import fields

# from app.authors import Author
from app.quotes import get_quotes, Quote
from app.utils import write_objects_to_csv


QUOTE_FIELDS = [quote_field.name for quote_field in fields(Quote)]
# AUTHOR_FIELDS = [author_field.name for author_field in fields(Author)]


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_objects_to_csv(quotes, output_csv_path, QUOTE_FIELDS)


if __name__ == "__main__":
    main("quotes.csv")
