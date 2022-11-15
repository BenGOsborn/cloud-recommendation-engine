import boto3
import botocore
import json
import utils

# NOTE initial params CANNOT be set to zero otherwise no gradients can be calculated
WEIGHTS_SIZE = 12
WEIGHTS_DEFAULT = json.dumps([0.5] * WEIGHTS_SIZE)
BIASES_DEFAULT = str(0.5)
CLUSTER_DEFAULT = str(0)


def lambda_handler(event, context):
    client = boto3.resource("dynamodb")

    users_table = client.Table("usersTable")
    users_params_table = client.Table("usersParamsTable")
    shows_table = client.Table("showsTable")
    shows_params_table = client.Table("showsParamsTable")

    for record in event["Records"]:
        body = json.loads(record["body"])
        user = body["user"]

        # Get scraped user data
        shows = utils.scrape(user)

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
                    "weights": WEIGHTS_DEFAULT,
                    "biases": BIASES_DEFAULT,
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
                        "weights": WEIGHTS_DEFAULT,
                        "biases": BIASES_DEFAULT,
                        "cluster": CLUSTER_DEFAULT
                    },
                    ConditionExpression="attribute_not_exists(showId)"
                )
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] != "ConditionalCheckFailedException":
                    raise
