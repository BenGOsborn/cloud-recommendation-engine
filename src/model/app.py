import utils
import json


def lambda_handler(event, context):
    # Load weights and biases from the request
    body = json.loads(event["body"])

    weights1_raw = body["weights1"]
    biases1_raw = body["biases1"]
    weights2_raw = body["weights2"]
    biases2_raw = body["biases2"]

    weights1, biases1, weights2, biases2 = utils.transform_data(
        weights1_raw,
        biases1_raw,
        weights2_raw,
        biases2_raw
    )

    print("Weights1", weights1)
    print("Biases1", biases1)
    print("Weights2", weights2)
    print("Biases1", biases2)

    # Make predictions
    predictions = utils.model(weights1, biases1, weights2, biases2)

    return {
        "statusCode": 200,
        "body": json.dumps(predictions.tolist())
    }


if __name__ == "__main__":
    event = {
        "body": json.dumps({
            "weights1": [[1, 0]],
            "biases1": [0],
            "weights2": [[0, 1]],
            "biases2": [0],
        })
    }

    predictions = lambda_handler(event, None)

    print(predictions)
