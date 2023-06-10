import scrapy
from scrapy.http import Response
from scrapy.crawler import CrawlerProcess
from dataclasses import dataclass


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        "https://quotes.toscrape.com/page/1/",
    ]

    def parse(self, response: Response, **kwargs) -> None:
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").get(),
                "author": quote.css("span small::text").get(),
                "tags": str(quote.css("div.tags a.tag::text").getall()).split(","),
            }

        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


def main(output_csv_path: str) -> None:
    process = CrawlerProcess(settings={
        "FEEDS": {
            output_csv_path: {"format": "csv"},
        },
    })

    process.crawl(QuotesSpider)
    process.start()


if __name__ == "__main__":
    main("quotes.csv")
