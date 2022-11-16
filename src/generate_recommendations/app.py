import boto3
import json
import os
import utils


def lambda_handler(event, context):
    db_client = boto3.resource("dynamodb")
    lambda_client = boto3.client("lambda")

    # Declare tables and resource names
    shows_params_table = db_client.Table(os.getenv("showsParamsTable"))
    recommendations_table = db_client.Table(os.getenv("recommendationsTable"))

    users_params_table_name = os.getenv("usersParamsTable")
    shows_table_name = os.getenv("showsTable")

    inference_model_function_name = os.getenv("inferenceModelFunction")

    # Get list of users
    users = []

    for record in event["Records"]:
        body = json.loads(record["body"])
        user = body["user"]

        users.append(user)

    # Get shows, show param, and user params from database
    shows, show_params, user_params = utils.fetch_data(
        users,
        db_client,
        shows_params_table,
        users_params_table_name,
        shows_table_name
    )

    # Make predictions from the weights and biases
    predictions = utils.make_predictions(
        lambda_client,
        inference_model_function_name,
        user_params,
        show_params
    )

    # Process and store recommendations
    utils.update_recommended(
        users,
        predictions,
        shows,
        recommendations_table
    )
