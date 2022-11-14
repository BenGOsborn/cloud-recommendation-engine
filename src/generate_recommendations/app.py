import boto3
import json


def lambda_handler(event, context):
    client = boto3.resource("dynamodb")

    users_table = client.Table("usersTable")
    shows_table = client.Table("showsTable")
    recommendations_table = client.Table("recommendationsTable")

    # Steps
    # 1. First select a random number of shows for all of the users (initially everything)
    # 2. Next get the full list of user and associated show params from the database
    # 3. Create the data matrix, have the model inference it
    # 4. Read the selected movies data and then assign them recommendations

    users_ = []

    for record in event["Records"]:
        body = json.loads(record["body"])
        user_ = body["user"]
        users_.append(user_)

    shows = shows_table.scan(Limit=100)
    users = users_table.batch_get_item(
        RequestItems=[
            {"userId": user} for user in users
        ]
    )

    print(shows)
    print(users)