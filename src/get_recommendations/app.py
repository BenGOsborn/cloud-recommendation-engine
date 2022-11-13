import boto3
import json


def lambda_handler(event, context):
    client = boto3.resource("dynamodb")

    recommendations_table = client.Table("recommendationsTable")

    # Get the recommendations for the user
    user = event["queryStringParameters"]["userId"]

    recommendations = recommendations_table.get_item(Key={
        "userId": user
    })

    return {
        "statusCode": 200,
        "body": json.dumps(recommendations)
    }
