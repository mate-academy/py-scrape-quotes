from app.parse_quotes import (
    parse_quotes,
    QUOTES_FIELDS,
    QUOTES_OUTPUT_CSV_PATH
)
from app.utils import write_data_to_csv


def main(output_csv_path: str) -> None:
    quotes = parse_quotes()
    write_data_to_csv(output_csv_path, quotes, QUOTES_FIELDS)


if __name__ == "__main__":
    main(QUOTES_OUTPUT_CSV_PATH)
