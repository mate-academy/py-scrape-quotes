import csv
import os
import sys
from dataclasses import dataclass, fields

import requests
from bs4 import BeautifulSoup

@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]

CSV_FIELDS = [field.name for field in fields(Quote)]

def main(output_csv_path: str) -> None:
    pass


if __name__ == "__main__":
    main("quotes.csv")
