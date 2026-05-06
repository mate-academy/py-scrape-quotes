import unicodedata


def format_name(name: str) -> str:
    # We decompose the characters: é -> e + accent
    normalized = unicodedata.normalize("NFD", name)
    # Remove all diacritics (category Mn)
    ascii_name = "".join(
        c for c in normalized if unicodedata.category(c) != "Mn"
    )

    parts = (
        ascii_name
        .replace("'", "")
        .translate(str.maketrans(".", " "))
        .split()
    )
    return "-".join(parts)
