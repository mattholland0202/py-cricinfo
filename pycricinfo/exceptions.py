"""Exceptions raised by the package."""

from typing import Optional


class CricinfoAPIException(Exception):  # noqa: N818 - renaming would break code that catches it
    """Raised when a request to Cricinfo returns a status code other than 200."""

    status_code: int
    route: str
    content: Optional[dict] = None

    def __init__(self, status_code: int, route: str, content: Optional[dict]) -> None:
        self.status_code = status_code
        self.route = route
        self.content = content
        super().__init__()

    def output(self) -> dict:
        """
        Output the exception details as a dictionary.

        Returns
        -------
        dict
            A dictionary containing the route, and content.
        """
        return {
            "route": self.route,
            "content": self.content,
        }

    def __str__(self) -> str:
        """Describe the status code, route and content of the failed request."""
        return f"CricinfoAPIException: status_code={self.status_code}, route={self.route}, content={self.content}"
