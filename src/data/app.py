import boto3
import json
import utils

WEIGHTS = json.dumps([0] * 12)
BIASES = json.dumps([0])


def lambda_handler(event, context):
    client = boto3.resource("dynamodb")

    ratings_table = client.Table("ratingsTable")
    users_table = client.Table("usersTable")
    shows_table = client.Table("showsTable")

    for record in event["Records"]:
        body = json.loads(record["body"])
        user = body["user"]

        data = utils.scrape(user)

        # **** We will also check that the user does not have weights - if they do we don't need to update them
        # **** Same with the movie - if the movie already has weights we do not need to update them
        # **** However, we can just update the rating freely

        # **** Also need to initialize new weights here

        # Insert into shows if it doesnt exist
        shows_table.put_item(
            Item={
                "showId": data["anime_id"],
                "animeTitle": data["anime_title"],
                "animeTitleEng": data["anime_title_eng"],
                "weights": WEIGHTS,
                "biases": BIASES
            },
            ConditionExpression="attribute_not_exists(showId)"
        )

        # Insert into users if it doesnt exist
        users_table.put_item(
            Item={
                "userId": user,
                "weights": WEIGHTS,
                "biases": BIASES
            },
            ConditionExpression="attribute_not_exists(userId)"
        )
