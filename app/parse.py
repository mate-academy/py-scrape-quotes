import csv
from datetime import datetime, date
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass, astuple, fields


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


@dataclass
class AuthorBio:
    name: str
    surname: str
    date_of_birth: date
    location: str
    description: str


authors_urls = set()
authors_bios: list[AuthorBio] = []

HOME_PAGE = "https://quotes.toscrape.com"
AUTHOR_PAGE = "https://quotes.toscrape.com/author/Albert-Einstein/"
QUOTE_FIELDS = [field.name for field in fields(Quote)]
AUTHOR_BIO_FIELDS = [field.name for field in fields(AuthorBio)]


def parse_single_author_bio(bio_soup: Tag) -> AuthorBio:
    full_name = bio_soup.select_one(".author-title").get_text(strip=True)
    name, *rest = full_name.split()
    surname = " ".join(rest)
    date_string = bio_soup.select_one(".author-born-date").get_text(strip=True)
    date_obj = datetime.strptime(date_string, "%B %d, %Y").date()
    location = bio_soup.select_one(
        ".author-born-location"
    ).get_text(strip=True)
    description = bio_soup.select_one(
        ".author-description"
    ).get_text(strip=True)

    return AuthorBio(
        name=name,
        surname=surname,
        date_of_birth=date_obj,
        location=location.replace("in ", ""),
        description=description,
    )


def create_author_bio(author_url_part: str) -> None:
    if author_url_part in authors_urls:
        return

    url = urljoin(HOME_PAGE, author_url_part)
    text = requests.get(url, timeout=10).text
    bio_soup = BeautifulSoup(text, "html.parser")

    bio = parse_single_author_bio(bio_soup)

    authors_urls.add(author_url_part)
    authors_bios.append(bio)


def parse_single_quote(quote: Tag) -> Quote:
    tags_block = quote.select_one("div[class='tags']")
    meta = tags_block.select_one("meta[content]")
    tags_info = meta["content"] if meta else ""
    tags = tags_info.split(",") if tags_info else []

    return Quote(
        text=quote.select_one("span[class='text']").get_text(strip=True),
        author=quote.select_one("small[class='author']").get_text(strip=True),
        tags=tags,
    )


def get_single_page_quotes(page_soup: Tag) -> list[Quote]:
    quotes = page_soup.select("div[class='quote']")
    result: list[Quote] = []

    for quote in quotes:
        link = quote.select_one("a")
        if link:
            create_author_bio(link["href"])

        result.append(parse_single_quote(quote))
    return result


def get_next_page_url(soup: BeautifulSoup) -> str | None:
    next_btn = soup.select_one("li.next a")
    return next_btn["href"] if next_btn else None


def get_all_quotes() -> list[Quote]:
    all_quotes: list[Quote] = []

    url = HOME_PAGE

    while url:
        text = requests.get(url, timeout=10).text
        soup = BeautifulSoup(text, "html.parser")

        all_quotes.extend(get_single_page_quotes(soup))

        next_page = get_next_page_url(soup)
        url = urljoin(HOME_PAGE, next_page) if next_page else None

    return all_quotes


def write_to_csv(path: str, data: list, field_names: list[str]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as _file:
        writer = csv.writer(_file)
        writer.writerow(field_names)
        writer.writerows([astuple(item) for item in data])


def main(
        output_csv_path: str,
        path_for_authors_bio: str | None = None
) -> None:
    authors_urls.clear()
    authors_bios.clear()

    quotes = get_all_quotes()
    write_to_csv(output_csv_path, quotes, QUOTE_FIELDS)

    if path_for_authors_bio:
        write_to_csv(path_for_authors_bio, authors_bios, AUTHOR_BIO_FIELDS)


if __name__ == "__main__":
    main("quotes.csv")
