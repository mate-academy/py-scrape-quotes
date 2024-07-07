from app.output_csv_path import get_quotes, write_quotes_to_csv


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_quotes_to_csv(output_csv_path, quotes)
    print("Quotes have been written")


if __name__ == "__main__":
    main("quotes.csv")
