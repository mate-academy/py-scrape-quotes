from dataclasses import dataclass, fields
import csv
import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin

BASE_URL = "https://quotes.toscrape.com/"


# --- Dataclass для цитаты ---
@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]  # строка с тегами, объединённая через запятую


# Заголовки CSV (title row)
PRODUCT_FIELDS = [field.name for field in fields(Quote)]


# --- Получаем количество страниц ---
def get_num_pages(page_soup: Tag) -> int:
    next_button = page_soup.select_one(".next a")
    if not next_button:
        return 1  # если кнопки "Next" нет — одна страница
    # На сайте quotes.toscrape.com кнопка ведёт на /page/2/
    # Мы можем просто пройти по страницам, пока next существует
    # (в main мы это реализуем без этой функции — для надёжности)
    return None  # placeholder, фактически не используем это значение напрямую


# --- Парсим одну цитату ---
def parse_single_product(quote: Tag) -> Quote:
    text = quote.select_one(".text").text.strip()
    author = quote.select_one(".author").text.strip()
    tags = [tag.text for tag in quote.select(".tags .tag")]
    return Quote(text=text, author=author, tags=tags)


# --- Парсим все цитаты на одной странице ---
def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select(".quote")  # каждый блок цитаты
    return [parse_single_product(quote) for quote in quotes]


# --- Собираем все страницы сайта ---
def get_all_quotes() -> list[Quote]:
    all_quotes = []
    next_page_url = BASE_URL

    while next_page_url:
        response = requests.get(next_page_url)
        soup = BeautifulSoup(response.text, "html.parser")

        # добавляем цитаты с текущей страницы
        all_quotes.extend(get_single_page_quotes(soup))

        # ищем ссылку на следующую страницу
        next_link = soup.select_one(".next a")
        if next_link:
            next_page_url = urljoin(BASE_URL, next_link["href"])
        else:
            next_page_url = None

    return all_quotes


# --- Записываем все цитаты в CSV ---
def write_quotes_to_csv(quotes: list[Quote], output_csv_path: str) -> None:
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows([
            [quote.text, quote.author, str(quote.tags)] for quote in quotes
        ])


# --- Основная функция ---
def main(output_csv_path: str) -> None:
    quotes = get_all_quotes()
    write_quotes_to_csv(quotes, output_csv_path)


if __name__ == "__main__":
    main("quotes.csv")
