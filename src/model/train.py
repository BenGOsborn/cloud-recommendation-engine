import utils
import json


def lambda_handler(event, context):
    # Load model params from the request
    body = json.loads(event["body"])

    weights1_raw = body["weights1"]
    biases1_raw = body["biases1"]
    weights2_raw = body["weights2"]
    biases2_raw = body["biases2"]
    target_raw = body["target"]
    mask_raw = body["mask"]

    # Convert raw params to tensors
    weights1, biases1, weights2, biases2, target, mask = [
        utils.to_tensor(raw_tensor, False) for raw_tensor in [
            weights1_raw,
            biases1_raw,
            weights2_raw,
            biases2_raw,
            target_raw,
            mask_raw,
        ]
    ]

    # Train model
    utils.fit(weights1, biases1, weights2, biases2, target, mask)

    return {
        "weights1": weights1.tolist(),
        "biases1": biases1.tolist(),
        "weights2": weights2.tolist(),
        "biases2": biases2.tolist(),
    }
