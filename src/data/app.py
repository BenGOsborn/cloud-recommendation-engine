import boto3
import botocore
import json
import utils
import random
import os


def lambda_handler(event, context):
    client = boto3.resource("dynamodb")

    # Initialize tables
    users_table = client.Table(os.getenv("usersTable"))
    users_params_table = client.Table(os.getenv("usersParamsTable"))
    shows_table = client.Table(os.getenv("showsTable"))
    shows_params_table = client.Table(os.getenv("showsParamsTable"))

    # **** We also need to consider the case of duplicates with this one

    users = []
    shows = []

    for record in event["Records"]:
        body = json.loads(record["body"])
        user = body["user"]

        # Get scraped user data
        users.append(user)
        shows.append(utils.scrape(user))

        # Store a list of reviewed shows from the user
        user_reviewed_shows = json.dumps([
            {
                "showId": show["anime_id"], "score": show["score"], "createdAt": show["created_at"]
            } for show in shows
        ])
        users_table.put_item(
            Item={
                "userId": user,
                "shows": user_reviewed_shows
            }
        )

        # Create weights and biases for users if they dont exist
        try:
            users_params_table.put_item(
                Item={
                    "userId": user,
                    "weights": json.dumps([random.random() for _ in range(WEIGHTS_SIZE)]),
                    "biases": str(random.random()),
                },
                ConditionExpression="attribute_not_exists(userId)"
            )
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                raise

        # Store metadata about each show
        for show in shows:
            shows_table.put_item(
                Item={
                    "showId": show["anime_id"],
                    "animeTitle": show["anime_title"],
                    "animeTitleEng": show["anime_title_eng"],
                }
            )

        # Create weights and biases for shows if they dont exist
        for show in shows:
            try:
                shows_params_table.put_item(
                    Item={
                        "showId": show["anime_id"],
                        "weights": json.dumps([random.random() for _ in range(WEIGHTS_SIZE)]),
                        "biases": str(random.random()),
                        "cluster": str(0),
                    },
                    ConditionExpression="attribute_not_exists(showId)"
                )
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                    raise
