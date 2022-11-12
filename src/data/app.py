import boto3
import json
import utils


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

        users_table.put_item(
            Item={"userId": user, "data": json.dumps(data)},
            ConditionExpression="attribute_not_exists(userId)"
        )
