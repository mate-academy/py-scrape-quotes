from dataclasses import dataclass

from app.authors import create_authors_csv_file, Author
from app.quotes import create_quotes_csv_file


# The class is only here for tests work properly
# but his copy is in the quotes.py
@dataclass
class Quote:
    text: str
    author: Author
    tags: list[str]


def main(output_csv_path: str) -> None:
    create_quotes_csv_file(output_csv_path)
    create_authors_csv_file()


if __name__ == "__main__":
    main("quotes.csv")
