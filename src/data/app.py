import boto3
import json
import utils

WEIGHTS_SIZE = 12
WEIGHTS = json.dumps([0] * WEIGHTS_SIZE)
BIASES = json.dumps([0])


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
            (show["anime_id"], show["score"], show["created_at"]) for show in shows
        ])
        users_table.put_item(
            Item={
                "userId": user,
                "shows": user_reviewed_shows
            }
        )

        # Create weights and biases for users if they dont exist
        users_params_table.put_item(
            Item={
                "userId": user,
                "weights": WEIGHTS,
                "biases": BIASES
            },
            ConditionExpression="attribute_not_exists(userId)"
        )

        # Store metadata about each show
        with shows_table.batch_writer() as writer:
            for show in shows:
                writer.put_item(
                    Item={
                        "showId": show["anime_id"],
                        "animeTitle": show["anime_title"],
                        "animeTitleEng": show["anime_title_eng"],
                    }
                )

        # Create weights and biases for shows if they dont exist
        with shows_params_table.batch_writer() as writer:
            for show in shows:
                writer.put_item(
                    Item={
                        "showId": show["anime_id"],
                        "weights": WEIGHTS,
                        "biases": BIASES
                    },
                    ConditionExpression="attribute_not_exists(showId)"
                )
