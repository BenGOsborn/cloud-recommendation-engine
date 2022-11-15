import boto3
import json
from boto3.dynamodb.conditions import Attr

MAX_SHOWS = 5
MAX_RECOMMENDATIONS = 20


def lambda_handler(event, context):
    db_client = boto3.resource("dynamodb")
    lambda_client = boto3.client("lambda")

    shows_params_table = db_client.Table("showsParamsTable")
    recommendations_table = db_client.Table("recommendationsTable")

    # Get list of users
    users = []

    for record in event["Records"]:
        body = json.loads(record["body"])
        user = body["user"]
        users.append(user)

    # Get list of show params
    show_params_res = shows_params_table.scan(
        FilterExpression=Attr("cluster").eq("0"),
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
        FunctionName="CloudRecommendationStack-inferenceModelFunction453-3HfaVvNKfXZQ",
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

    # Process predictions and recommend movies
    for i in range(len(predictions)):
        temp_shows = [
            (prediction, shows[j]) for j, prediction in enumerate(predictions[i])
        ]
        temp_shows = sorted(temp_shows, key=lambda x: x[0], reverse=True)
        temp_shows = temp_shows[:MAX_RECOMMENDATIONS]

        recommendations_table.put_item(Item={
            "userId": users[i],
            "recommended": json.dumps(temp_shows)
        })
