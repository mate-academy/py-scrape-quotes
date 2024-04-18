import csv
from dataclasses import asdict
from typing import List

from app.models import Quote


def write_quotes_to_csv(
        output_csv_path: str, quotes_obj_list: List[Quote]
) -> None:
    with open(
            output_csv_path,
            mode="w",
            newline="",
            encoding="utf-8",
    ) as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=["text", "author", "tags"])

        writer.writeheader()

        for quote in quotes_obj_list:
            writer.writerow(asdict(quote))
