import boto3
import json
import utils

WEIGHTS = json.dumps([0] * 12)
BIASES = json.dumps([0])


def lambda_handler(event, context):
    client = boto3.resource("dynamodb")

    ratings_table = client.Table("ratingsTable")
    users_table = client.Table("usersTable")
    users_params_table = client.Table("usersParamsTable")
    shows_table = client.Table("showsTable")
    shows_params_table = client.Table("showsParamsTable")

    for record in event["Records"]:
        body = json.loads(record["body"])
        user = body["user"]

        data = utils.scrape(user)

        # **** Hold on, consider that there are multiple data items that need to be inserted ?

        users_table.put_item(
            Item={
                "userId": user,
                "records": json.dumps()
            }
        )

        ratings_table.put_item(
            Item={
                "showId": data["anime_id"]
            }
        )

        # Insert into shows if it doesnt exist
        shows_params_table.put_item(
            Item={
                "showId": data["anime_id"],
                "weights": WEIGHTS,
                "biases": BIASES
            },
            ConditionExpression="attribute_not_exists(showId)"
        )

        # Insert into users if it doesnt exist
        users_params_table.put_item(
            Item={
                "userId": user,
                "weights": WEIGHTS,
                "biases": BIASES
            },
            ConditionExpression="attribute_not_exists(userId)"
        )
