from typing import Dict, List
import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://myanimelist.net/animelist"


# Extract the specified traits from the data
def extract_traits(data: Dict[str, str], traits: List[str]):
    out = {}

    for trait in traits:
        if trait in data:
            out[trait] = str(data[trait])
        else:
            return None

    return out


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

    traits_to_extract = [
        "anime_id",
        "anime_title",
        "anime_title_eng",
        "score",
        "created_at"
    ]

    for row in items:
        traits = extract_traits(row, traits_to_extract)

        if traits is None:
            continue

        out.append(traits)

    return out
