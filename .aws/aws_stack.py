from aws_cdk import (
    Duration,
    Stack,
    aws_dynamodb as dynamodb_,
    aws_sqs as sqs_,
    aws_apigateway as apigateway_,
    aws_iam as iam_,
    aws_lambda as lambda_,
    aws_lambda_event_sources as event_source_
)
from constructs import Construct
import os


class CloudRecommendationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ==== Data sync / scraper ====

        # DynamoDB tables
        ratings_table = dynamodb_.Table(
            self,
            id="ratingsTable",
            table_name="ratingsTable",
            partition_key=dynamodb_.Attribute(
                name="id",
                type=dynamodb_.AttributeType.STRING
            )
        )
        users_table = dynamodb_.Table(
            self,
            id="usersTable",
            table_name="usersTable",
            partition_key=dynamodb_.Attribute(
                name="userId",
                type=dynamodb_.AttributeType.STRING
            )
        )
        users_params_table = dynamodb_.Table(
            self,
            id="usersParamsTable",
            table_name="usersParamsTable",
            partition_key=dynamodb_.Attribute(
                name="userId",
                type=dynamodb_.AttributeType.STRING
            )
        )
        shows_table = dynamodb_.Table(
            self,
            id="showsTable",
            table_name="showsTable",
            partition_key=dynamodb_.Attribute(
                name="showId",
                type=dynamodb_.AttributeType.STRING
            )
        )
        shows_params_table = dynamodb_.Table(
            self,
            id="showsParamsTable",
            table_name="showsParamsTable",
            partition_key=dynamodb_.Attribute(
                name="showId",
                type=dynamodb_.AttributeType.STRING
            )
        )

        # Integrate sqs directly with API gateway
        sync_request_queue = sqs_.Queue(self, "syncRequestQueue")
        api_gateway_role = iam_.Role(
            self,
            id="syncRequestQueueAPIGateway",
            assumed_by=iam_.ServicePrincipal("apigateway.amazonaws.com")
        )
        sync_request_queue.grant_send_messages(api_gateway_role)

        # API gateway SQS integration
        api_gateway = apigateway_.RestApi(self, "recommendationApi")
        api_gateway_sqs_integration = apigateway_.AwsIntegration(
            service="sqs",
            path=f"{os.getenv('CDK_DEFAULT_ACCOUNT')}/{sync_request_queue.queue_name}",
            integration_http_method="POST",
            options=apigateway_.IntegrationOptions(
                credentials_role=api_gateway_role,
                request_parameters={
                    "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
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
        sync_data_resource = api_gateway.root.add_resource("syncData")
        sync_data_resource.add_method(
            "POST",
            api_gateway_sqs_integration,
            method_responses=[
                {"statusCode": "200"},
                {"statusCode": "400"},
                {"statusCode": "500"}
            ]
        )

        # Lambda scraper integrated with SQS
        scraper = lambda_.DockerImageFunction(
            self,
            "scraperFunction",
            code=lambda_.DockerImageCode.from_image_asset(
                os.path.join(os.getcwd(), "..", "src", "data")
            ),
            timeout=Duration.seconds(10)
        )
        scraper.add_event_source(
            event_source_.SqsEventSource(sync_request_queue)
        )
        ratings_table.grant_read_write_data(scraper)
        users_table.grant_read_write_data(scraper)
        users_params_table.grant_read_write_data(scraper)
        shows_table.grant_read_write_data(scraper)
        shows_params_table.grant_read_write_data(scraper)

        # ==== Recommendation engine ====

        # ==== Request recommendations ====

        # ==== Training ====
