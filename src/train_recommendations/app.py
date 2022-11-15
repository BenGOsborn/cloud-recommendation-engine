import boto3
import json


BATCH_SIZE = 50


def lambda_handler(event, context):
    # Steps
    # 1. Get a batch of users and their associated shows and normalize this data
    # 2. Merge the two into a single set of weights and biases and keep track of shows seen for each
    # 3. For shows one person hasnt seen, construct a mask matrix
    # 4. Train the model on the given shows and users
    # 5. Get the new weights and biases for the users and update them in the params tables

    db_client = boto3.resource("dynamodb")
    lambda_client = boto3.client("lambda")

    users_table = db_client.Table("usersTable")

    # Get a random sample of users
    users_res = users_table.scan(
        Limit=BATCH_SIZE
    )
    users = users_res["Items"] if "Items" in users_res else []

    # Keep a record of the frequency a show appears
    show_freq = {}

    for i, user in enumerate(users):
        shows_list = json.loads(user["shows"])

        for show in shows_list:
            show_id = show["showId"]

            if show_id not in show_freq:
                show_freq[show_id] = {}

            show_freq[show_id][i] = True

    # Sort the frequencies of the shows and get the highest amount
    shows = sorted(
        [(k, len(v)) for k, v in show_freq.items()],
        key=lambda x: x[0],
        reverse=True
    )[:BATCH_SIZE]

    print(shows)

    # **** So now we will filter through all of these responses and keep track of the highest recorded movies, select them, and then determine if other users had the same thing
    # **** To do this efficiently we will need to keep some sort of reverse mapping between users of who had what (we can just keep a true false map for each movie)
