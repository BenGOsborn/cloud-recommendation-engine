from typing import Dict, List
import requests
from bs4 import BeautifulSoup
import json
import random
import botocore

BASE_URL = "https://myanimelist.net/animelist"
WEIGHT_SIZE = 12


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

    return items


# Generate random weights and biases
def create_params(weight_size: int):
    weights = json.dumps([2 * random.random() - 1 for _ in range(weight_size)])
    bias = str(2 * random.random() - 1)

    return weights, bias


# Insert the user data
def create_user_data(users: List[str], shows: List, users_table: any):
    with users_table.batch_writer() as writer:
        for i in range(len(users)):
            user_reviewed_shows = json.dumps([
                {
                    "showId": show["anime_id"],
                    "score": show["score"],
                    "createdAt": show["created_at"],
                } for show in shows[i]
            ])

            writer.put_item(
                Item={
                    "userId": users[i],
                    "shows": user_reviewed_shows
                }
            )


# Create the user params if they dont exist
def create_user_params(users: List[str], users_params_table: any):
    for user in users:
        try:
            weights, bias = create_params(WEIGHT_SIZE)

            users_params_table.put_item(
                Item={
                    "userId": user,
                    "weights": weights,
                    "biases": bias,
                },
                ConditionExpression="attribute_not_exists(userId)"
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise


# Insert the shows data (assumed that there are no duplicates)
def create_show_data(shows: List, shows_table: any):
    with shows_table.batch_writer() as writer:
        for show in shows:
            writer.put_item(
                Item={
                    "showId": str(show["anime_id"]),
                    "animeTitle": show["anime_title"],
                    "animeTitleEng": show["anime_title_eng"],
                }
            )


# Create the show params if they dont exist
def create_show_params(shows: List[str], shows_params_table: any):
    for show in shows:
        try:
            weights, bias = create_params(WEIGHT_SIZE)

            shows_params_table.put_item(
                Item={
                    "showId": str(show["anime_id"]),
                    "weights": weights,
                    "biases": bias
                },
                ConditionExpression="attribute_not_exists(showId)"
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise
