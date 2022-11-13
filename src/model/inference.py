import utils
import json


def lambda_handler(event, context):
    # Load model params from the request
    print(event)

    body = json.loads(event["body"])

    weights1_raw = body["weights1"]
    biases1_raw = body["biases1"]
    weights2_raw = body["weights2"]
    biases2_raw = body["biases2"]

    # Convert raw params to tensors
    weights1, biases1, weights2, biases2 = [
        utils.to_tensor(raw_tensor, False) for raw_tensor in [
            weights1_raw,
            biases1_raw,
            weights2_raw,
            biases2_raw
        ]
    ]

    # Make predictions
    predictions = utils.model(weights1, biases1, weights2, biases2)

    return {
        "statusCode": 200,
        "body": json.dumps(predictions.tolist())
    }
