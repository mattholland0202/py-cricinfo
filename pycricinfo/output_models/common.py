import re

from prettytable import PrettyTable

SNAKE_CASE_REGEX = re.compile(r"(?<!^)(?=[A-Z])")


class HeaderlessTableMixin:
    def print_headerless_table(self, rows: list[tuple[str, bool]]):
        """
        Print a PrettyTable with no header, with rows matching the supplied data

        Parameters
        ----------
        rows : list[tuple[str, bool]]
            The rows of data to print. Each tuple contains the data to print,
            and whether to include a divider between tows
        """
        table = PrettyTable()
        table.header = False
        for row in rows:
            table.add_row([row[0]], divider=row[1])
        print(table)
