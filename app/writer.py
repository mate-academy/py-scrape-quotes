import csv
import os
from dataclasses import astuple


class FileWriter:
    def __init__(self, path, columns):
        self.path = path
        self.columns = columns
        self._check_file_exist()

    def _check_file_exist(self):
        if not os.path.exists(self.path):
            with open(
                    self.path,
                    mode="w",
                    encoding="UTF8",
                    newline=""
            ) as file:
                writer = csv.writer(file)
                writer.writerow(self.columns)

    @staticmethod
    def _get_elements(elements):
        if not isinstance(elements, (list, tuple)):
            return (elements, )

        return elements

    def write_elements(self, elements):
        elements = self._get_elements(elements)
        with open(self.path, mode="a", encoding="UTF8", newline="") as file:
            writer = csv.writer(file)
            writer.writerows([astuple(element) for element in elements])
