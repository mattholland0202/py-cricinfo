class CricinfoAPIException(Exception):
    status_code: int
    route: str
    content: dict | None = None

    def __init__(self, status_code: int, route: str, content: dict | None):
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
