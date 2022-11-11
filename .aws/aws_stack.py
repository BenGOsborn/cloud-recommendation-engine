from aws_cdk import (
    # Duration,
    Stack,
    aws_dynamodb as dynamodb,
    aws_sqs as sqs,
    aws_apigateway as apigateway,
    aws_iam as iam,
)
from constructs import Construct
import os


class CloudRecommendationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ==== Data sync / scraper ====

        # Store ratings
        ratings_table = dynamodb.Table(self,
                                       id="ratingsTable",
                                       table_name="ratingsTable",
                                       partition_key=dynamodb.Attribute(
                                           name="id",
                                           type=dynamodb.AttributeType.STRING
                                       )
                                       )

        # Integrate sqs directly with API gateway
        sync_request_queue = sqs.Queue(self, "syncRequestQueue")
        api_gateway_role = iam.Role(
            self,
            "syncRequestQueueAPIGateway",
            iam.ServicePrincipal("apigateway.amazonaws.com")
        )
        sync_request_queue.grant_send_messages(api_gateway_role)

        # API gateway SQS integration
        api_gateway = apigateway.RestApi(self, "api")
        api_gateway_sqs_integration = apigateway.AwsIntegration(
            service="sqs",
            path=f"{os.getenv('CDK_DEFAULT_ACCOUNT')}/{sync_request_queue.queue_name}"
            integration_http_method="POST"
            options=apigateway.IntegrationOptions(
                credentials_role=api_gateway_role,
                request_parameters={
                    "integration.request.header.Content-Type": "application/x-www-form-urlencoded"
                },
                request_templates={
                    "application/json": "Action=SendMessage&MessageBody=$input.body"
                },
                integration_responses=[
                    {"statusCode": "200"},
                    {"statusCode": "400"},
                    {"statusCode": "500"}
                ]
            )
        )
        api_gateway.root.add_method(
            "POST",
            api_gateway_sqs_integration,
            method_responses=[
                {"statusCode": "200"},
                {"statusCode": "400"},
                {"statusCode": "500"}
            ]
        )

        # ==== Recommendation engine ====

        # ==== Request recommendations ====

        # ==== Training ====
