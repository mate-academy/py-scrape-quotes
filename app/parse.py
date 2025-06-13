from dataclasses import dataclass

# ToDo:
@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def main(output_csv_path: str) -> None:
    pass


if __name__ == "__main__":
    main("quotes.csv")
