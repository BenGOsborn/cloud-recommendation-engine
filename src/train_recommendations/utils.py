from typing import List
import json

BATCH_SIZE = 50


# Get a random sample of users
def sample_users(users_table: any):
    users_res = users_table.scan(Limit=BATCH_SIZE)
    users = users_res["Items"] if "Items" in users_res else []

    return users


# Get a list of top shows and the frequency they occur
def get_top_shows(users: List["str"]):
    shows_freq = {}

    for i, user in enumerate(users):
        shows_list = json.loads(user["shows"])

        for show in shows_list:
            show_id = show["showId"]

            if show_id not in shows_freq:
                shows_freq[show_id] = {}

            shows_freq[show_id][i] = float(show["score"])

    # Sort the frequencies of the shows and get the highest amount
    shows_freq_list = sorted(
        [(k, len(v)) for k, v in shows_freq.items()],
        key=lambda x: x[1],
        reverse=True
    )[:BATCH_SIZE]

    return shows_freq, shows_freq_list


# Fetch the user and show params
def fetch_data(users: List, shows_freq_list: List, db_client: any, users_params_table_name: str, shows_params_table_name: str):
    batch_res = db_client.batch_get_item(
        RequestItems={
            users_params_table_name: {
                "Keys": [
                    {"userId": user["userId"]} for user in users
                ]
            },
            shows_params_table_name: {
                "Keys": [
                    {"showId": show[0]} for show in shows_freq_list
                ]
            }
        }
    )
    batch = batch_res["Responses"]

    user_params = batch["usersParamsTable"]
    show_params = batch["showsParamsTable"]

    return user_params, show_params
