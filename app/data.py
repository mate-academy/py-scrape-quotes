from dataclasses import dataclass, fields


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


COLUMNS = [field.name for field in fields(Quote)]
