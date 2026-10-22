"""Shared helpers for printing output models as tables."""

import re

from prettytable import PrettyTable

SNAKE_CASE_REGEX = re.compile(r"(?<!^)(?=[A-Z])")
""" Regex to identify positions between lower and uppercase letters, for camel to snake case conversion """


class HeaderlessTableMixin:
    """Mixin which prints rows of text as a table with no header."""

    def print_headerless_table(self, rows: list[tuple[str, bool]]) -> None:
        """
        Print a PrettyTable with no header, with rows matching the supplied data.

        Parameters
        ----------
        rows : list[tuple[str, bool]]
            The rows of data to print. Each tuple contains the data to print,
            and whether to include a divider after the row (True) or not (False).
        """
        table = PrettyTable()
        table.header = False
        for row in rows:
            table.add_row([row[0]], divider=row[1])
        print(table)  # noqa: T201 - printing the table is the purpose of this method
