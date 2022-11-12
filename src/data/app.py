import boto3
import json
import utils


def lambda_handler(event, context):
    client = boto3.resource("dynamodb")
    table = client.Table("ratingsTable")

    for record in event["Records"]:
        body = json.loads(record["body"])
        user = body["user"]

        data = utils.scrape(user)

        table.put_item(
            Item={"userId": user, "data": json.dumps(data)}
        )
