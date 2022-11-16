import boto3
import json
import utils
import os


def lambda_handler(event, context):
    client = boto3.resource("dynamodb")

    # Initialize tables
    users_table = client.Table(os.getenv("usersTable"))
    users_params_table = client.Table(os.getenv("usersParamsTable"))
    shows_table = client.Table(os.getenv("showsTable"))
    shows_params_table = client.Table(os.getenv("showsParamsTable"))

    # Create a list of users and shows
    users = []
    shows = []

    seen_shows = {}
    show_set = []

    for record in event["Records"]:
        body = json.loads(record["body"])
        user = body["user"]

        # Store user and associated shows
        users.append(user)

        scraped = utils.scrape(user)
        shows.append(scraped)

        # Store a set of shows
        for show in scraped:
            show_id = show["anime_id"]

            if show_id not in seen_shows:
                show_set.append(show)
                seen_shows[show_id] = True

    # Process and store data
    utils.create_user_data(users, shows, users_table)
    utils.create_user_params(users, users_params_table)
    utils.create_show_data(show_set, shows_table)
    utils.create_show_params(show_set, shows_params_table)
