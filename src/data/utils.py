import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://myanimelist.net/animelist"


# Scrape list of rated shows from user profile
def scrape(user: str):
    # Get the raw content
    url = f"{BASE_URL}/{user}?status=2"

    out = requests.get(url)
    soup = BeautifulSoup(out.text, features="html.parser")

    tag = soup.find("table", {"class": "list-table"})
    items = json.loads(tag["data-items"])

    # Extract required traits from the html
    out = []

    for row in items:
        temp = []

        traits = ["anime_id", "anime_title", "anime_title_eng", "score"]

        for trait in traits:
            temp.append(row[trait] if trait in row else None)

        out.append(temp)

    return out
