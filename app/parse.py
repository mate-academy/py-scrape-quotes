from dataclasses import dataclass
import requests
import bs4
import csv


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com/page/{}/"
    quotes = []
    page = 1

    while True:
        url = base_url.format(page)
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = bs4.BeautifulSoup(response.text, "html.parser")

        quote_elements = soup.select("div.quote")
        if not quote_elements:
            break

        for quote in quote_elements:
            text = quote.select_one("span.text").text
            author = quote.select_one("small.author").text
            tags = [tag.text for tag in quote.select("div.tags > a.tag")]
            quotes.append(Quote(text, author, tags))

        print(f"Scraped page {page}")
        page += 1

    print(f"Total quotes scraped: {len(quotes)}")

    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in quotes:
            tags_str = repr(quote.tags)
            writer.writerow([quote.text, quote.author, tags_str])


if __name__ == "__main__":
    main("quotes.csv")
