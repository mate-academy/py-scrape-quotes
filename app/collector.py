from bs4 import BeautifulSoup

from app.data import Quote


def collect_items(content: bytes) -> list[Quote]:
    quotes = []

    parser = BeautifulSoup(content, "html.parser")

    for quote in parser.select(".quote"):
        text = quote.select_one(".text").text
        author = quote.select_one(".author").text
        tags = [tag.text for tag in quote.select(".tag")]

        quotes.append(
            Quote(
                text=text,
                author=author,
                tags=tags
            )
        )

    return quotes
