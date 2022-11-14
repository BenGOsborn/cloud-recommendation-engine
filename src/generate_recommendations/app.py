import boto3
import json
from boto3.dynamodb.conditions import Attr

MAX_SHOWS = 5


def lambda_handler(event, context):
    db_client = boto3.resource("dynamodb")
    lambda_client = boto3.resource("lambda")

    shows_table = db_client.Table("showsTable")
    shows_params_table = db_client.Table("showsParamsTable")
    recommendations_table = db_client.Table("recommendationsTable")

    # Steps
    # 1. First select a random number of shows for all of the users (initially everything)
    # 2. Next get the full list of user and associated show params from the database
    # 3. Create the data matrix, have the model inference it
    # 4. Read the selected movies data and then assign them recommendations

    users = []

    for record in event["Records"]:
        body = json.loads(record["body"])
        user = body["user"]
        users.append(user)

    # Get list of show params
    show_params_res = shows_params_table.scan(
        FilterExpression=Attr("cluster").eq(0),
        Limit=MAX_SHOWS
    )
    show_params = show_params_res["Items"] if "Items" in show_params_res else [
    ]

    # Get user params and shows
    batch_res = db_client.batch_get_item(
        RequestItems={
            "usersParamsTable": {
                "Keys": [
                    {"userId": user} for user in users
                ]
            },
            "showsTable": {
                "Keys": [
                    {"showId": show["showId"]} for show in show_params
                ]
            }
        }
    )
    batch = batch_res["Responses"]

    user_params = batch["usersParamsTable"]
    shows = batch["showsTable"]

    # Make predictions from the weights and biases
    weights1 = [json.loads(params["weights"]) for params in user_params]
    biases1 = [float(params["biases"]) for params in user_params]
    weights2 = [json.loads(params["weights"]) for params in show_params]
    biases2 = [float(params["biases"]) for params in show_params]

    results = lambda_client.invoke(
        FunctionName="CloudRecommendationStack-generateRecommendationsFu-Jhy7LBXUaEXH",
        InvocationType="RequestResponse",
        Payload=json.dumps({
            "weights1": weights1,
            "biases1": biases1,
            "weights2": weights2,
            "biases2": biases2
        })
    )

    print(results)
