import boto3
import json
from boto3.dynamodb.conditions import Attr

MAX_SHOWS = 5


def lambda_handler(event, context):
    client = boto3.resource("dynamodb")

    shows_table = client.Table("showsTable")
    shows_params_table = client.Table("showsParamsTable")
    recommendations_table = client.Table("recommendationsTable")

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
    batch_res = client.batch_get_item(
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

    print(show_params)
    print(user_params)
    print(shows)

    # Merge the weights and params together
    weights1 = user_params
