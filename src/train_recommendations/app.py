import boto3
import json


BATCH_SIZE = 50


def lambda_handler(event, context):
    # Steps
    # 1. Get a batch of users and their associated shows and normalize this data
    # 2. Merge the two into a single set of weights and biases and keep track of shows seen for each
    # 3. For shows one person hasnt seen, construct a mask matrix
    # 4. Train the model on the given shows and users
    # 5. Get the new weights and biases for the users and update them in the params tables

    db_client = boto3.resource("dynamodb")
    lambda_client = boto3.client("lambda")

    users_table = db_client.Table("usersTable")

    # Get a random sample of users
    users_res = users_table.scan(
        Limit=BATCH_SIZE
    )
    users = users_res["Items"] if "Items" in users_res else []

    # Keep a record of the frequency a show appears
    show_freq = {}

    for i, user in enumerate(users):
        shows_list = json.loads(user["shows"])

        for show in shows_list:
            show_id = show["showId"]

            if show_id not in show_freq:
                show_freq[show_id] = {}

            show_freq[show_id][i] = float(show["score"])

    # Sort the frequencies of the shows and get the highest amount
    shows_freq_list = sorted(
        [(k, len(v)) for k, v in show_freq.items()],
        key=lambda x: x[0],
        reverse=True
    )[:BATCH_SIZE]

    # Get the params from the given users and shows
    batch_res = db_client.batch_get_item(
        RequestItems={
            "usersParamsTable": {
                "Keys": [
                    {"userId": user["userId"]} for user in users
                ]
            },
            "showsParamsTable": {
                "Keys": [
                    {"showId": show[0]} for show in shows_freq_list
                ]
            }
        }
    )
    batch = batch_res["Responses"]

    user_params = batch["usersParamsTable"]
    show_params = batch["showsParamsTable"]

    # Create training outputs and mask
    training_matrix = []
    mask = []

    for i in range(len(user_params)):
        temp_training_matrix = []
        temp_mask = []

        for j in range(len(show_params)):
            show_id = shows_freq_list[j][0]

            if i not in show_freq[show_id]:
                temp_training_matrix.append(0)
                temp_mask.append(1)
            else:
                temp_training_matrix.append(show_freq[show_id][i] / 10)
                temp_mask.append(0)

        training_matrix.append(temp_training_matrix)
        mask.append(temp_mask)

    print(training_matrix)
    print(mask)
