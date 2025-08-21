from app.author import AUTHOR_FIELDS
from app.parse_biographies import get_authors
from app.parse_quotes import get_quotes
from app.quote import QUOTE_FIELDS
from app.utils import write_elements_to_csv


def main(output_csv_path: str) -> None:
    write_elements_to_csv(
        elements=get_quotes(), path=output_csv_path, fields=QUOTE_FIELDS
    )


if __name__ == "__main__":
    main("quotes.csv")
    write_elements_to_csv(
        elements=get_authors(), path="biographies.csv", fields=AUTHOR_FIELDS
    )
