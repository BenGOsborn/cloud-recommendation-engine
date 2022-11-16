import boto3
import json
import os
import utils


def lambda_handler(event, context):
    db_client = boto3.resource("dynamodb")
    lambda_client = boto3.client("lambda")

    # Declare tables and resource names
    users_table = db_client.Table(os.getenv("usersTable"))

    users_params_table = db_client.Table(os.getenv("usersParamsTable"))
    shows_params_table = db_client.Table(os.getenv("showsParamsTable"))

    users_params_table_name = os.getenv("usersParamsTable")
    shows_params_table_name = os.getenv("showsParamsTable")

    train_model_function_name = os.getenv("trainModelFunction")

    # Get a random sample of users
    users = utils.sample_users(users_table)

    # Get show frequencies and a list of top shows
    shows_freq, shows_freq_list = utils.get_top_shows(users)

    # Get the user and show paramsk
    user_params, show_params = utils.fetch_data(
        users,
        shows_freq_list,
        db_client,
        users_params_table_name,
        shows_params_table_name
    )

    # get the trained params

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

    # Update the params with the new params
    with users_params_table.batch_writer() as writer:
        for i in range(len(user_params)):
            writer.put_item(
                Item={
                    "userId": users[i]["userId"],
                    "weights": json.dumps(new_weights1[i]),
                    "biases": str(new_biases1[i]),
                })

    with shows_params_table() as writer:
        for i in range(len(show_params)):
            writer.put_item(
                Item={
                    "showId": shows_freq_list[i][0],
                    "weights": json.dumps(new_weights2[i]),
                    "biases": str(new_biases2[i]),
                    "cluster": show_params[i]["cluster"],
                }
            )
