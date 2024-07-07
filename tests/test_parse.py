import csv
from pathlib import Path

from app.parse import main
from app.output_csv_path import Quote

BASE_DIR = Path(__file__).resolve().parent

CORRECT_QUOTES_CSV_PATH = BASE_DIR / "correct_quotes.csv"


def test_main():
    path = "result.csv"
    main(path)

    with open(CORRECT_QUOTES_CSV_PATH, "r") as correct_file, open(
        path, "r"
    ) as result_file:
        correct_reader = csv.reader(correct_file)
        result_reader = csv.reader(result_file)

        for correct_row in correct_reader:
            result_row = next(result_reader)

            correct_quote = Quote(*correct_row)
            result_row = Quote(*result_row)

            assert correct_quote.text == result_row.text
            assert correct_quote.author == result_row.author
            assert correct_quote.tags == result_row.tags
