import boto3
import json

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

    # Get list of shows to rate
    shows_response = shows_table.scan(Limit=MAX_SHOWS)
    shows = shows_response["Items"] if "Items" in shows_response else []

    # Get params
    params_response = client.batch_get_item(
        RequestItems={
            "usersParamsTable": {
                "Keys": [
                    {"userId": user} for user in users
                ]
            },
            "showsParamsTable": {
                "Keys": [
                    {"showId": show["showId"]} for show in shows
                ]
            }
        }
    )
    params = params_response["Responses"]

    user_params = params["usersParamsTable"]
    show_params = params["showsParamsTable"]
