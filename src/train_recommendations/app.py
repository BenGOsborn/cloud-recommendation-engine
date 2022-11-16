import boto3
import json
import os
import utils


def lambda_handler(event, context):
    db_client = boto3.resource("dynamodb")
    lambda_client = boto3.client("lambda")

    # Declare tables and resource names
    users_table = db_client.Table(os.getenv("usersTable"))

    users_params_table = db_client.Table(os.getenv("usersParamsTable"))
    shows_params_table = db_client.Table(os.getenv("showsParamsTable"))

    users_params_table_name = os.getenv("usersParamsTable")
    shows_params_table_name = os.getenv("showsParamsTable")

    train_model_function_name = os.getenv("trainModelFunction")

    # Get a random sample of users
    users = utils.sample_users(users_table)

    # Get show frequencies and a list of top shows
    shows_freq, shows_freq_list = utils.get_top_shows(users)

    # Get the user and show paramsk
    user_params, show_params = utils.fetch_data(
        users,
        shows_freq_list,
        db_client,
        users_params_table_name,
        shows_params_table_name
    )

    # Get the params
    new_weights1, new_biases1, new_weights2, new_biases2 = utils.train_params(
        user_params,
        show_params,
        shows_freq,
        shows_freq_list,
        lambda_client,
        train_model_function_name
    )

    # Save updated params
    utils.save_params(
        users,
        shows_freq_list,
        new_weights1,
        new_biases1,
        new_weights2,
        new_biases2,
        users_params_table,
        shows_params_table
    )
