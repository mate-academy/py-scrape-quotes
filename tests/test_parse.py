import ast
import csv
from pathlib import Path

from app.parse import main, Quote

BASE_DIR = Path(__file__).resolve().parent

CORRECT_QUOTES_CSV_PATH = BASE_DIR / "correct_quotes.csv"


def parse_tags(field: str):
    """Safely parse the tags column from CSV."""
    if not field:
        return []
    try:
        # Try to parse it as a Python literal (e.g., "['life', 'love']")
        value = ast.literal_eval(field)
        if isinstance(value, list):
            return value
        # If it's a single string value, wrap it in a list
        return [str(value)]
    except (ValueError, SyntaxError):
        # Fallback: split by commas (e.g., "life, love")
        return [t.strip() for t in field.split(",") if t.strip()]


def test_main():
    """Test that generated CSV matches the correct reference CSV."""
    path = "result.csv"
    main(path)

    with open(CORRECT_QUOTES_CSV_PATH, "r", encoding="utf-8") as correct_file, open(
        path, "r", encoding="utf-8"
    ) as result_file:
        correct_reader = csv.reader(correct_file)
        result_reader = csv.reader(result_file)

        for correct_row in correct_reader:
            result_row = next(result_reader)

            correct_quote = Quote(
                text=correct_row[0],
                author=correct_row[1],
                tags=parse_tags(correct_row[2]),
            )

            result_quote = Quote(
                text=result_row[0],
                author=result_row[1],
                tags=parse_tags(result_row[2]),
            )

            assert correct_quote.text == result_quote.text
            assert correct_quote.author == result_quote.author
            assert correct_quote.tags == result_quote.tags
