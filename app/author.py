from dataclasses import dataclass, fields
from datetime import datetime


@dataclass
class Author:
    name: str
    birth_date: datetime
    birth_location: str
    description: str


AUTHOR_FIELDS = [field.name for field in fields(Author)]
