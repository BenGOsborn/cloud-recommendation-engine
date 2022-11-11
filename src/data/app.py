import boto3
import json


def lambda_handler(event, context):
    dynamodb = boto3.client("dynamodb")
    table_name = "ratingsTable"

    for record in event["Records"]:
        body = record["body"]

        print(body)
