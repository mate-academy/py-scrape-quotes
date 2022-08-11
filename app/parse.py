from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
import csv



@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def main(output_csv_path: str) -> None:
    i = 1
    while True:

        site = requests.get(f"https://quotes.toscrape.com/page/{i}").content
        soup = BeautifulSoup(site, "html.parser")
        all_quotes = soup.select('.quote')
        for quote in all_quotes:
            all_tags = []
            text = quote.select_one('.text').text
            author = quote.select_one('.author').text
            tags = quote.select('.tag')
            for tag in tags:
                tag_content = tag.text
                all_tags.append(tag_content)
            quote = Quote(text=text, author=author, tags=all_tags)
            #data = f"{quote.text}, {quote.author}"
            # with open("output.csv", "w", newline='', encoding='utf-8') as csvfile:
            #     writer = csv.writer(csvfile)
            #     writer.writerow(data)
        next = soup.find('nav').find("li", {"class": "next"})
        if not next:
            break
        i += 1

print(main('quotes.csv'))
# if __name__ == "__main__":
#     main("quotes.csv")
