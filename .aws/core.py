from aws_cdk import (
    Duration,
    aws_dynamodb as dynamodb_,
    aws_sqs as sqs_,
    aws_apigateway as apigateway_,
    aws_iam as iam_,
)


# Create dynamodb tables
def create_tables(self):
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

    recommendations_table = dynamodb_.Table(
        self,
        id="recommendationsTable",
        table_name="recommendationsTable",
        partition_key=dynamodb_.Attribute(
            name="userId",
            type=dynamodb_.AttributeType.STRING
        )
    )

    return users_table, users_params_table, shows_table, shows_params_table, recommendations_table


# Create API gateway
def create_api(self):
    api_gateway_role = iam_.Role(
        self,
        id="sqsAPIGatewayRole",
        assumed_by=iam_.ServicePrincipal("apigateway.amazonaws.com")
    )
    api_gateway = apigateway_.RestApi(self, "recommendationApi")

    return api_gateway_role, api_gateway


# Create queues
def create_sqs(self, api_gateway_role: iam_.Role):
    sync_data_queue = sqs_.Queue(
        self,
        "syncDataQueue",
        visibility_timeout=Duration.minutes(10)
    )
    sync_data_queue.grant_send_messages(api_gateway_role)

    generate_recommendations_queue = sqs_.Queue(
        self,
        "generateRecommendationsQueue",
        visibility_timeout=Duration.minutes(10)
    )
    generate_recommendations_queue.grant_send_messages(api_gateway_role)

    return sync_data_queue, generate_recommendations_queue
