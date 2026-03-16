import csv

from requests import Session
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, field, astuple
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}

BASE_URL = 'http://quotes.toscrape.com/'
LOGIN_URL = 'http://quotes.toscrape.com/login'



@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

def login(session: Session):
    response = session.get(LOGIN_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'lxml')
    token_input = soup.find("input", {"name": "csrf_token"})
    if not token_input:
        return
    token = token_input.get("value")
    data = {
        "csrf_token": token,
        "username": "noname",
        "password": "password"}
    session.post(
        LOGIN_URL,
        headers=HEADERS,
        data=data,
        allow_redirects=True)

def parse_single_quote(quote_html: Tag) -> Quote:
    tags = [tag.get_text(strip=True) for tag in quote_html.select(".tags .tag")]
    return Quote(
        text=quote_html.select_one(".text").get_text(strip=True),
        author=quote_html.select_one(".author").get_text(strip=True),
        tags=tags,
    )


def get_quotes(session: Session, url: str) -> tuple[list[Quote], str | None]:
    response = session.get(url, headers=HEADERS)
    if response.status_code != 200:
        return [], None
    soup = BeautifulSoup(response.text, 'lxml')
    quotes_html = soup.find_all("div", class_="quote")

    quotes = [parse_single_quote(quote) for quote in quotes_html]

    next_button = soup.select_one("li.next > a")
    next_page = next_button.get("href") if next_button else None
    return quotes, next_page

def write_quotes_to_csv(quotes: list[Quote], path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for quote in quotes:
            writer.writerow(astuple(quote))

def main(output_path: str = "quotes.csv") -> None:
    all_quotes = []
    current_url = BASE_URL

    with Session() as session:
        login(session)
        while current_url:
            print(f"Parsing {current_url}")
            quotes, next_page_relative = get_quotes(session, current_url)
            all_quotes.extend(quotes)
            if next_page_relative:
                current_url = urljoin(BASE_URL, next_page_relative)
            else:
                current_url = None
    if all_quotes:
        write_quotes_to_csv(all_quotes, output_path)
        print(f"Successfully parsed {len(all_quotes)} quotes")
    else:
        print("No quotes found")


if __name__ == "__main__":
     main("quotes.csv")
