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
    all_the_quotes = []
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
            one_quote = [quote.text, quote.author, quote.tags]
            all_the_quotes.append(one_quote)
        i += 1
        next = soup.find('nav').find("li", {"class": "next"})
        if not next:
            break
    student_header = ['name', 'age', 'major', 'minor']
    with open(output_csv_path, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(student_header)
        writer.writerows(all_the_quotes)


if __name__ == "__main__":
    main("quotes.csv")
