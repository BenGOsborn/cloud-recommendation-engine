import utils
import json


def lambda_handler(event, context):
    # Load model params from the request
    body = json.loads(event["body"])

    weights1_raw = body["weights1"]
    biases1_raw = body["biases1"]
    weights2_raw = body["weights2"]
    biases2_raw = body["biases2"]

    # Convert raw params to tensors
    weights1 = utils.to_tensor(weights1_raw, False)
    biases1 = utils.to_tensor(biases1_raw, False)
    weights2 = utils.to_tensor(weights2_raw, False)
    biases2 = utils.to_tensor(biases2_raw, False)

    # Make predictions
    predictions = utils.model(weights1, biases1, weights2, biases2)

    return {
        "predictions": predictions.tolist()
    }
