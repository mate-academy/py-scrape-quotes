import csv


def save_to_file(path: str, columns: tuple, data: list) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(
            (quote.text, quote.author, quote.tags)
            for quote in data
        )
