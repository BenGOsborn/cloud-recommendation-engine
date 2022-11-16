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
    print(
        {
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

    user_params = batch[users_params_table_name]
    show_params = batch[shows_params_table_name]

    return user_params, show_params


def train_params(
    user_params: List,
    show_params: List,
    shows_freq: any,
    shows_freq_list: List,
    lambda_client: any,
    train_model_function_name: str
):
    # Get the params
    weights1 = [json.loads(params["weights"]) for params in user_params]
    biases1 = [float(params["biases"]) for params in user_params]
    weights2 = [json.loads(params["weights"]) for params in show_params]
    biases2 = [float(params["biases"]) for params in show_params]

    # Create training outputs and mask
    target = []
    mask = []

    for i in range(len(user_params)):
        temp_target = []
        temp_mask = []

        for j in range(len(show_params)):
            show_id = shows_freq_list[j][0]

            if i not in shows_freq[show_id]:
                temp_target.append(0)
                temp_mask.append(1)
            else:
                temp_target.append(shows_freq[show_id][i] / 10)
                temp_mask.append(0)

        target.append(temp_target)
        mask.append(temp_mask)

    # Train the params
    results = lambda_client.invoke(
        FunctionName=train_model_function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps({
            "body": json.dumps({
                "weights1": weights1,
                "biases1": biases1,
                "weights2": weights2,
                "biases2": biases2,
                "target": target,
                "mask": mask
            })
        })
    )

    new_params = json.loads(
        results["Payload"].read().decode("utf-8")
    )

    new_weights1 = new_params["weights1"]
    new_biases1 = new_params["biases1"]
    new_weights2 = new_params["weights2"]
    new_biases2 = new_params["biases2"]

    return new_weights1, new_biases1, new_weights2, new_biases2


# Save the updated params
def save_params(
    users: List,
    shows_freq_list: List,
    weights1: List,
    biases1: List,
    weights2: List,
    biases2: List,
    users_params_table: any,
    shows_params_table: any
):
    # Update the params with the new params
    with users_params_table.batch_writer() as writer:
        for i in range(len(weights1)):
            writer.put_item(
                Item={
                    "userId": users[i]["userId"],
                    "weights": json.dumps(weights1[i]),
                    "biases": str(biases1[i]),
                })

    with shows_params_table() as writer:
        for i in range(len(weights2)):
            writer.put_item(
                Item={
                    "showId": shows_freq_list[i][0],
                    "weights": json.dumps(weights2[i]),
                    "biases": str(biases2[i]),
                }
            )
