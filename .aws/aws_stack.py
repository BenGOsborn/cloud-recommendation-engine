from aws_cdk import (
    # Duration,
    Stack,
    aws_dynamodb as dynamodb,
    # aws_sqs as sqs,
)
from constructs import Construct


class AwsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Data sync / scraper

        # Recommendation engine

        # Request recommendations

        # Training

        # example resource
        # queue = sqs.Queue(
        #     self, "AwsQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
