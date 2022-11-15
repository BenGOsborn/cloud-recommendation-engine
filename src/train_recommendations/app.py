import boto3
import json


def lambda_handler(event, context):
    # Steps
    # 1. Get a batch of users and their associated shows and normalize this data
    # 2. Merge the two into a single set of weights and biases and keep track of shows seen for each
    # 3. For shows one person hasnt seen, construct a mask matrix
    # 4. Train the model on the given shows and users
    # 5. Get the new weights and biases for the users and update them in the params tables

    pass
