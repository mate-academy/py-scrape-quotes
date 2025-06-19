import csv
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
import time


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class AuthorBio:
    name: str
    born_date: str
    born_location: str
    description: str


def get_quotes_from_page(soup: BeautifulSoup) -> list[Quote]:
    """
    Парсить одну сторінку з цитатами та повертає список об'єктів Quote.
    """
    quotes_data = []
    for quote_div in soup.find_all("div", class_="quote"):
        text = quote_div.find("span", class_="text").get_text(strip=True)
        author = quote_div.find("small", class_="author").get_text(strip=True)
        tags = [tag.get_text(strip=True)
                for tag in quote_div.find(
                "div", class_="tags").find_all("a", class_="tag")]
        quotes_data.append(Quote(text=text, author=author, tags=tags))
    return quotes_data


def get_author_bio(author_url: str) -> AuthorBio:
    """
    Збирає біографію автора з його сторінки.
    """
    response = requests.get(author_url)
    response.raise_for_status()  # Перевіряємо, чи був запит успішним
    soup = BeautifulSoup(response.text, "html.parser")

    author_details_div = soup.find(
        "div",
        class_="author-details",
    )
    name = author_details_div.find(
        "h3",
        class_="author-title",
    ).get_text(strip=True)
    born_date = author_details_div.find(
        "span",
        class_="author-born-date",
    ).get_text(strip=True)
    born_location = author_details_div.find(
        "span",
        class_="author-born-location",
    ).get_text(strip=True)
    description = author_details_div.find(
        "div",
        class_="author-description").get_text(strip=True)

    return AuthorBio(name=name, born_date=born_date,
                     born_location=born_location, description=description)


def main(output_csv_path: str) -> None:
    base_url = "https://quotes.toscrape.com"
    all_quotes: list[Quote] = []
    author_bios: dict[str, AuthorBio] = {}  # Кеш для біографій авторів
    page_number = 1

    print("Починаємо збір цитат...")

    while True:
        url = f"{base_url}/page/{page_number}/"
        print(f"Збираємо дані зі сторінки: {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Помилка при запиті до {url}: {e}")
            break  # Припиняємо, якщо є проблема з мережею або сервером

        soup = BeautifulSoup(response.text, "html.parser")

        quotes_on_page = get_quotes_from_page(soup)
        if not quotes_on_page:
            # Немає цитат на сторінці, ймовірно, досягли кінця пагінації
            print(f"Кінець пагінації на сторінці "
                  f"{page_number}. Знайдено 0 цитат.")
            break

        all_quotes.extend(quotes_on_page)

        # Збір біографій авторів (додаткове завдання)
        for quote_div in soup.find_all("div", class_="quote"):
            author_name = quote_div.find("small",
                                         class_="author").get_text(strip=True)
            if author_name not in author_bios:
                author_link = quote_div.find("a")["href"]
                full_author_url = f"{base_url}{author_link}"
                print(f"Збираємо біографію для {author_name} з "
                      f"{full_author_url}")
                try:
                    author_bios[author_name] = get_author_bio(full_author_url)
                except requests.exceptions.RequestException as e:
                    print(f"Помилка при зборі біографії для "
                          f"{author_name}: {e}")
                time.sleep(0.5)  # Будьте обережні з ресурсами сайту

        next_button = soup.find("li", class_="next")
        if not next_button:
            print("Кінець пагінації. Кнопки 'Next' не знайдено.")
            break  # Немає кнопки "Next", досягли кінця

        page_number += 1
        time.sleep(1)  # Затримка між запитами до сторінок

    print(f"\nЗібрано {len(all_quotes)} цитат.")
    print(f"Зібрано {len(author_bios)} унікальних біографій авторів.")

    # Запис цитат у CSV-файл
    try:
        with open(
                output_csv_path,
                "w",
                newline="",
                encoding="utf-8",
        ) as csvfile:
            fieldnames = ["text", "author", "tags"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for quote in all_quotes:
                writer.writerow({
                    "text": quote.text,
                    "author": quote.author,
                    "tags": str(quote.tags)
                })
        print(f"Цитати успішно збережено у файлі: {output_csv_path}")
    except IOError as e:
        print(f"Помилка запису цитат у файл {output_csv_path}: {e}")

    # Запис біографій авторів у окремий CSV-файл (додаткове завдання)
    author_bio_csv_path = "author_bios.csv"
    try:
        with open(
                author_bio_csv_path,
                "w", newline="",
                encoding="utf-8",
        ) as csvfile:
            fieldnames = ["name", "born_date", "born_location", "description"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for author_name, bio in author_bios.items():
                writer.writerow({
                    "name": bio.name,
                    "born_date": bio.born_date,
                    "born_location": bio.born_location,
                    "description": bio.description
                })
        print(f"Біографії авторів успішно збережено у файлі: "
              f"{author_bio_csv_path}")
    except IOError as e:
        print(f"Помилка запису біографій авторів у файл "
              f"{author_bio_csv_path}: {e}")


if __name__ == "__main__":
    main("quotes.csv")
