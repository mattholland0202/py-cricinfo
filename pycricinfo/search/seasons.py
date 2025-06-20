import re
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from pycricinfo.config import get_settings


def get_matches_in_season(season_name: str, fetch: bool = True):
    folder = Path(get_settings().api_response_output_folder)
    folder = folder / "seasons"
    folder.mkdir(parents=True, exist_ok=True)
    file_path = (folder / f"{str(season_name)}.html").resolve()

    if fetch:
        session = requests.Session()

        session.headers["User-Agent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:138.0) Gecko/20100101 Firefox/138.0"
        )

        session.headers["Referer"] = "https://www.espncricinfo.com/ci/engine/series/index.html"

        session.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"

        season_page = session.get(
            f"https://www.espncricinfo.com/ci/engine/series/index.html?season={quote(str(season_name))};view=season"
        ).content

        with open(file_path, "w") as file:
            file.write(str(season_page))

    return parse_season_html(file_path)


def parse_season_html(file_path: Path):
    with open(file_path, "r") as file:
        content = file.read()

    content = re.sub(r"^b\'|\'$", "", content)

    soup = BeautifulSoup(content, "html.parser")

    series_blocks = soup.find_all("section", class_="series-summary-block collapsed")

    series_list = []
    for block in series_blocks:
        anchor = block.find("a")

        title = anchor.contents[0]
        title = re.sub(r"\\", "", title)
        title = re.sub(r"\s{2,}|\n|\r", " ", title).strip()

        series_id = block.get("data-series-id")
        summary_url = block.get("data-summary-url")

        link = anchor.get("href", "")

        series_list.append({"title": title, "id": series_id, "link": link, "summary_url": summary_url})

    return series_list
