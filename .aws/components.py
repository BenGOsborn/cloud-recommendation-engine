from aws_cdk import (
    Duration,
    aws_dynamodb as dynamodb_,
    aws_sqs as sqs_,
    aws_apigateway as apigateway_,
    aws_iam as iam_,
    aws_lambda as lambda_,
    aws_lambda_event_sources as event_source_,
    aws_events as events,
    aws_events_targets as targets,
)
import os


# Create data sync component
def create_data_sync(
    self,
    api_gateway_role: iam_.Role,
    api_gateway: apigateway_.RestApi,
    sync_data_queue: sqs_.Queue,
    users_table: dynamodb_.Table,
    users_params_table: dynamodb_.Table,
    shows_table: dynamodb_.Table,
    shows_params_table: dynamodb_.Table
):
    api_gateway_sync_data_sqs_integration = apigateway_.AwsIntegration(
        service="sqs",
        path=f"{os.getenv('CDK_DEFAULT_ACCOUNT')}/{sync_data_queue.queue_name}",
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
        api_gateway_sync_data_sqs_integration,
        method_responses=[
            {"statusCode": "200"},
            {"statusCode": "400"},
            {"statusCode": "500"}
        ]
    )

    scraper_function = lambda_.DockerImageFunction(
        self,
        "scraperFunction",
        code=lambda_.DockerImageCode.from_image_asset(
            os.path.join(os.getcwd(), "..", "src", "data")
        ),
        timeout=Duration.minutes(10),
        environment={
            "usersTable": users_table.table_name,
            "usersParamsTable": users_params_table.table_name,
            "showsTable": shows_table.table_name,
            "showsParamsTable": shows_params_table.table_name,
        }
    )
    scraper_function.add_event_source(
        event_source_.SqsEventSource(sync_data_queue)
    )

    users_table.grant_read_write_data(scraper_function)
    users_params_table.grant_read_write_data(scraper_function)
    shows_table.grant_read_write_data(scraper_function)
    shows_params_table.grant_read_write_data(scraper_function)


# Create the inference model NOTE should be deployed with SageMaker
def create_inference_model(self):
    inference_model_function = lambda_.DockerImageFunction(
        self,
        "inferenceModelFunction",
        code=lambda_.DockerImageCode.from_image_asset(
            os.path.join(os.getcwd(), "..", "src", "model"),
            file="inference.Dockerfile"
        ),
        timeout=Duration.minutes(10)
    )

    return inference_model_function


# Create the training model NOTE should be deployed with SageMaker
def create_training_model(self):
    train_model_function = lambda_.DockerImageFunction(
        self,
        "trainModelFunction",
        code=lambda_.DockerImageCode.from_image_asset(
            os.path.join(os.getcwd(), "..", "src", "model"),
            file="train.Dockerfile"
        ),
        timeout=Duration.minutes(10)
    )

    return train_model_function


# Generate recommendations component
def create_generate_recommendations(
    self,
    api_gateway_role: iam_.Role,
    api_gateway: apigateway_.RestApi,
    generate_recommendations_queue: sqs_.Queue,
    recommendations_table: dynamodb_.Table,
    users_params_table: dynamodb_.Table,
    shows_table: dynamodb_.Table,
    shows_params_table: dynamodb_.Table,
    inference_model_function: lambda_.Function
):
    generate_recommendations_resource = api_gateway.root.add_resource(
        "generateRecommendations"
    )

    api_gateway_generate_recommendations_sqs_integration = apigateway_.AwsIntegration(
        service="sqs",
        path=f"{os.getenv('CDK_DEFAULT_ACCOUNT')}/{generate_recommendations_queue.queue_name}",
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
    generate_recommendations_resource.add_method(
        "POST",
        api_gateway_generate_recommendations_sqs_integration,
        method_responses=[
            {"statusCode": "200"},
            {"statusCode": "400"},
            {"statusCode": "500"}
        ]
    )

    # Lambda recommendations function
    generate_recommendations_function = lambda_.DockerImageFunction(
        self,
        "generateRecommendationsFunction",
        code=lambda_.DockerImageCode.from_image_asset(
            os.path.join(
                os.getcwd(), "..", "src", "generate_recommendations"
            )
        ),
        timeout=Duration.minutes(10),
        environment={
            "showsParamsTable": shows_params_table.table_name,
            "recommendationsTable": recommendations_table.table_name,
            "usersParamsTable": users_params_table.table_name,
            "showsTable": shows_table.table_name,
            "inferenceModelFunction": inference_model_function.function_name
        }
    )

    generate_recommendations_function.add_event_source(
        event_source_.SqsEventSource(generate_recommendations_queue)
    )

    recommendations_table.grant_read_write_data(
        generate_recommendations_function
    )
    users_params_table.grant_read_data(
        generate_recommendations_function
    )
    shows_table.grant_read_data(
        generate_recommendations_function
    )
    shows_params_table.grant_read_data(
        generate_recommendations_function
    )

    inference_model_function.grant_invoke(
        generate_recommendations_function
    )


# Create get recommendations component
def create_get_recommendations(
    self,
    api_gateway: apigateway_.RestApi,
    recommendations_table: dynamodb_.Table,
):
    get_recommendations_function = lambda_.DockerImageFunction(
        self,
        "getRecommendationsFunction",
        code=lambda_.DockerImageCode.from_image_asset(
            os.path.join(os.getcwd(), "..", "src", "get_recommendations")
        ),
        timeout=Duration.seconds(10),
        environment={
            "recommendationsTable": recommendations_table.table_name
        }
    )
    recommendations_table.grant_read_data(get_recommendations_function)
    get_recommendations_function_integration = apigateway_.LambdaIntegration(
        get_recommendations_function,
        request_templates={
            "application/json": "{\"statusCode\": \"200\"}"
        }
    )
    get_recommendations_resource = api_gateway.root.add_resource(
        "getRecommendations"
    )
    get_recommendations_resource.add_method(
        "GET",
        get_recommendations_function_integration
    )


# Create train recommendation model component
def create_train_recommendation_model(
    self,
    users_table: dynamodb_.Table,
    users_params_table: dynamodb_.Table,
    shows_params_table: dynamodb_.Table,
    train_model_function: lambda_.Function,
):
    train_recommendations_function = lambda_.DockerImageFunction(
        self,
        "trainRecommendationsFunction",
        code=lambda_.DockerImageCode.from_image_asset(
            os.path.join(os.getcwd(), "..", "src", "train_recommendations")
        ),
        timeout=Duration.minutes(10),
        environment={
            "usersTable": users_table.table_name,
            "usersParamsTable": users_params_table.table_name,
            "showsParamsTable": shows_params_table.table_name,
            "trainModelFunction": train_model_function.function_name
        }
    )
    users_table.grant_read_data(
        train_recommendations_function
    )
    users_params_table.grant_read_write_data(
        train_recommendations_function
    )
    shows_params_table.grant_read_write_data(
        train_recommendations_function
    )
    train_model_function.grant_invoke(
        train_recommendations_function
    )

    # Setup recurring event bridge
    events.Rule(
        self,
        "scheduleTrain",
        rule_name="scheduleTrain",
        targets=[
            targets.LambdaFunction(handler=train_recommendations_function)
        ],
        schedule=events.Schedule.rate(Duration.hours(2))
    )
