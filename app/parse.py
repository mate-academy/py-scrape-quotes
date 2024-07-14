import csv
import time
import requests
from bs4 import BeautifulSoup

from app.settings import Quote, BASE_URL


def parse_one_quote(quote_soup: BeautifulSoup) -> Quote:
    tags = [tag.text for tag in quote_soup.select("a.tag")]
    return Quote(
        text=quote_soup.select_one(".text").text.strip(),
        author=quote_soup.select_one(".author").text.strip(),
        tags=tags,
    )


def parse_quotes() -> list[Quote]:
    num = 1
    quotes = []
    page_num = 1

    while True:
        print(f"\nParsing page {page_num}...")
        response = requests.get(f"{BASE_URL}/page/{page_num}/")
        if response.status_code != 200:
            break

        page_soup = BeautifulSoup(response.content, "html.parser")
        quote_soups = page_soup.select(".quote")

        if not quote_soups:
            break

        for quote_soup in quote_soups:
            quotes.append(parse_one_quote(quote_soup))
            print(f"\tParsing quote {num}...")
            num += 1

        page_num += 1

    print("\nParsing pages finished.\n")
    return quotes


def write_quotes_to_file(quotes: list[Quote], output_csv_path: str) -> None:
    num = 1
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["text", "author", "tags"])

        for quote in quotes:
            writer.writerow([quote.text, quote.author, quote.tags])
            print(f"Writing the parsed quote {num}...")
            num += 1

    print("\nWriting the parsed quotes to .csv finished.")


def main(output_csv_path: str) -> None:
    print("=== Parsing Quotes ===")
    print("Parsing quotes...\n")
    quotes = parse_quotes()
    print(
        "-------------------------------------\n"
        "Writing parsed quotes to .csv file...\n"
    )
    write_quotes_to_file(quotes, output_csv_path)


if __name__ == "__main__":
    start = time.perf_counter()
    main("quotes.csv")
    end = time.perf_counter()
    print(f"\nSpent time: {end - start}")
