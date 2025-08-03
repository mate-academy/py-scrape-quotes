import requests
from bs4 import BeautifulSoup
import time
import csv
from dataclasses import dataclass

BASE_URL = 'https://quotes.toscrape.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

def parse_page(url):
    time.sleep(1)  # Delay to be gentle
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return [], None
        soup = BeautifulSoup(response.text, 'html.parser')
        quotes = []
        for quote_div in soup.find_all('div', class_='quote'):
            text_span = quote_div.find('span', class_='text')
            text = text_span.get_text(strip=True) if text_span else None
            author_small = quote_div.find('small', class_='author')
            author = author_small.get_text(strip=True) if author_small else None
            tags_div = quote_div.find('div', class_='tags')
            tags = []
            if tags_div:
                tags = [tag.get_text(strip=True) for tag in tags_div.find_all('a', class_='tag')]
            if text and author:
                quotes.append(Quote(text, author, tags))
        next_button = soup.find('li', class_='next')
        next_url = None
        if next_button:
            next_link = next_button.find('a', href=True)
            if next_link:
                next_url = BASE_URL + next_link['href']
        return quotes, next_url
    except Exception:
        return [], None

def main(output_csv_path: str) -> None:
    all_quotes = []
    current_url = BASE_URL
    while current_url:
        quotes, next_url = parse_page(current_url)
        all_quotes.extend(quotes)
        current_url = next_url
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['text', 'author', 'tags'])
        for quote in all_quotes:
            tags_str = ';'.join(quote.tags)
            writer.writerow([quote.text, quote.author, tags_str])

if __name__ == "__main__":
    print(main("quotes.csv"))