import boto3
import json
import utils


def lambda_handler(event, context):
    dynamodb = boto3.client("dynamodb")
    table_name = "ratingsTable"

    for record in event["Records"]:
        body = record["body"]
        user = body["user"]

        data = utils.scrape(user)
        dynamodb.put_item(
            TableName=table_name,
            Item={"userId": {"S": json.dumps(data)}}
        )
