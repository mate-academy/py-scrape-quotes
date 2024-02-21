from app.scrapper import QuoteScrapper


def main(output_csv_path: str) -> None:
    quote_scrapper = QuoteScrapper()
    quotes = quote_scrapper.get_all_quotes()

    quote_scrapper.write_quotes_to_csv(
        csv_path=output_csv_path, quotes=quotes
    )


if __name__ == "__main__":
    main("quotes.csv")
