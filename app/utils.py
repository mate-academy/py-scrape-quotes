import csv
from dataclasses import astuple


def write_objects_to_csv(quotes: list,
                         csv_path: str,
                         object_fields: list) -> None:
    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(object_fields)
        writer.writerows([astuple(quote) for quote in quotes])
