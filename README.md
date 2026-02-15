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

Также собирайте биографию автора для каждой цитаты (или даже разделяйте её в другой CSV-файл). 
Конечно, здесь не стоит несколько раз загружать одну и ту же страницу для одного и того же автора (кэшировать).