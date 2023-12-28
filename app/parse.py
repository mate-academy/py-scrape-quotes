from app.file_handlers import write_quotes
from app.loggers import configure_logging
from app.quotes import get_quotes


def main(output_csv_path: str) -> None:
    configure_logging()
    quotes = get_quotes()
    write_quotes(quotes=quotes, file_path=output_csv_path)


if __name__ == "__main__":
    main("output_csv")
