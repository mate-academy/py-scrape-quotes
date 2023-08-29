from app.description import BASE_URL, EXT_URL_QUOTE, QUOTES_FILE, AUTHORS_FILE

from app.quote_parse_logic import get_quote_from_all_pages, write_quote_to_file
from app.author_parse_logic import (
    get_authors_from_all_pages,
    write_author_to_file
)


def main(output_csv_quote_path: str, output_csv_author_path: str) -> None:
    quotes_list = get_quote_from_all_pages(BASE_URL, EXT_URL_QUOTE)

    for quote in quotes_list:
        write_quote_to_file(output_csv_quote_path, quote)

    authors_dict = get_authors_from_all_pages(BASE_URL, EXT_URL_QUOTE)

    for author in authors_dict.values():
        write_author_to_file(output_csv_author_path, author)


if __name__ == "__main__":
    main(QUOTES_FILE, AUTHORS_FILE)
