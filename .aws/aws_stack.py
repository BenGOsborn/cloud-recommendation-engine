from aws_cdk import (
    # Duration,
    Stack,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_apigateway as apigateway,
)
from constructs import Construct


class CloudRecommendationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Data sync / scraper
        ratings_table = dynamodb.Table(self,
                                       id="ratingsTable",
                                       table_name="ratingsTable",
                                       partition_key=dynamodb.Attribute(
                                           name="id",
                                           type=dynamodb.AttributeType.STRING
                                       )
                                       )

        sync_request_queue = sqs.Queue(self, "syncRequestQueue")

        # Recommendation engine

        # Request recommendations

        # Training
