# Scrape quotes

- Read [the guideline](https://github.com/mate-academy/py-task-guideline/blob/main/README.md) before start


## Task

In this task you will parse https://quotes.toscrape.com/ website to get list of 
all quotes from it. This site uses pagination to show data, but you still have to 
get all quotes - so to scrape all pages. Each quote should consist of `text`, 
`author` and `tags` - the classes structure already implemented in `app/parse.py`.

You need to write `main` function, which takes `output_csv_path` - it's a file, that should
be created, and in which all data about quotes should be written.


Hints:
- keep your code as simple as possible;
- write reusable functions;
- be gentle to website resources.


### Optional task

Also collect author's biography for each quote (or even separate it to another csv file). 
Of course here you should not load the same page for the same author several times (cache it).

### Author parse

add imports to parse.py
```
from app.description import AUTHORS_FILE
from app.author_parse_logic import (
    get_authors_from_all_pages,
    write_author_to_file
 )
```
add few strings of code to main func
```
authors_dict = get_authors_from_all_pages(BASE_URL, EXT_URL_QUOTE)

for author in authors_dict.values():
    write_author_to_file(output_csv_author_path, author)
  
```
change main function
```
def main(output_csv_quote_path: str, output_csv_author_path: str) -> None:

main(QUOTES_FILE, AUTHORS_FILE)

```
