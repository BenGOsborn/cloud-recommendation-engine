import boto3
import json


BATCH_SIZE = 50


def lambda_handler(event, context):
    db_client = boto3.resource("dynamodb")
    lambda_client = boto3.client("lambda")

    users_table = db_client.Table("usersTable")

    users_params_table = db_client.Table("usersParamsTable")
    shows_params_table = db_client.Table("showsParamsTable")

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

            if i not in show_freq[show_id]:
                temp_target.append(0)
                temp_mask.append(1)
            else:
                temp_target.append(show_freq[show_id][i] / 10)
                temp_mask.append(0)

        target.append(temp_target)
        mask.append(temp_mask)

    # Train the params
    results = lambda_client.invoke(
        FunctionName="CloudRecommendationStack-trainModelFunction579FF5A-KtqZ0LNXgDmc",
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

    # Update the params
    for i in range(len(user_params)):
        users_params_table.put_item(
            Item={
                "userId": users[i]["userId"],
                "weights": json.dumps(new_weights1[i]),
                "biases": str(new_biases1[i]),
            })

    for i in range(len(show_params)):
        shows_params_table.put_item(
            Item={
                "showId": shows_freq_list[i][0],
                "weights": json.dumps(new_weights2[i]),
                "biases": str(new_biases2[i]),
                "cluster": show_params[i]["cluster"],
            }
        )
