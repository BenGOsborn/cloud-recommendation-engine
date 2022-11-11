import requests
from bs4 import BeautifulSoup
import json


def scrape(user: str, page: int):
    url = "https://myanimelist.net/animelist/Armaterasu"

    out = requests.get(url)
    soup = BeautifulSoup(out.text, features="html.parser")

    tag = soup.find("table", {"class": "list-table"})
    items = json.loads(tag["data-items"])

    for row in items:
        print(
            row["anime_id"],
            row["anime_title"],
            row["anime_title_eng"],
            row["score"], "\n"
        )


if __name__ == "__main__":
    scrape(None, None)
