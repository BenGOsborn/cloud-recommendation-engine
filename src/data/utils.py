import requests
from bs4 import BeautifulSoup
import json


def scrape(user: str, page: int):
    url = "https://myanimelist.net/animelist/Armaterasu"

    out = requests.get(url)
    soup = BeautifulSoup(out.text, features="html.parser")

    tag = soup.find_all("table")
    print(tag[0])


if __name__ == "__main__":
    scrape(None, None)
