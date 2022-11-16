from typing import List
import json


MAX_SHOWS = 50
MAX_RECOMMENDATIONS = 50


# Sample shows, show params, and user params from the table
def fetch_data(
    users: List[str],
    db_client: any,
    shows_params_table: any,
    users_params_table_name: str,
    shows_table_name: str
):
    show_params_res = shows_params_table.scan(Limit=MAX_SHOWS)
    show_params = show_params_res["Items"] if "Items" in show_params_res else [
    ]

    batch_res = db_client.batch_get_item(
        RequestItems={
            users_params_table_name: {
                "Keys": [
                    {"userId": user} for user in users
                ]
            },
            shows_table_name: {
                "Keys": [
                    {"showId": show["showId"]} for show in show_params
                ]
            }
        }
    )
    batch = batch_res["Responses"]

    user_params = batch["usersParamsTable"]
    shows = batch["showsTable"]

    return shows, show_params, user_params


# Make predictions from the given data
def make_predictions(
    lambda_client: any,
    inference_model_function_name: str,
    user_params: List,
    show_params: List
):
    weights1 = [json.loads(params["weights"]) for params in user_params]
    biases1 = [float(params["biases"]) for params in user_params]
    weights2 = [json.loads(params["weights"]) for params in show_params]
    biases2 = [float(params["biases"]) for params in show_params]

    results = lambda_client.invoke(
        FunctionName=inference_model_function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps({
            "body": json.dumps({
                "weights1": weights1,
                "biases1": biases1,
                "weights2": weights2,
                "biases2": biases2
            })
        })
    )

    predictions = json.loads(
        results["Payload"].read().decode("utf-8")
    )["predictions"]

    return predictions


# Update the recommended movies given the predictions
def update_recommended(users: List[str], predictions: List, shows: List, recommendations_table: any):
    recommended = []

    for i in range(len(predictions)):
        temp_shows = [
            (prediction, shows[j]) for j, prediction in enumerate(predictions[i])
        ]
        temp_shows = sorted(temp_shows, key=lambda x: x[0], reverse=True)
        temp_shows = temp_shows[:MAX_RECOMMENDATIONS]

        recommended.append(temp_shows)

    with recommendations_table.batch_writer() as writer:
        writer.put_item(Item={
            "userId": users[i],
            "recommended": json.dumps(temp_shows)
        })
