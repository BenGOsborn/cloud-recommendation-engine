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
    weights1 = utils.to_tensor(weights1_raw, True)
    biases1 = utils.to_tensor(biases1_raw, True)
    weights2 = utils.to_tensor(weights2_raw, True)
    biases2 = utils.to_tensor(biases2_raw, True)
    target = utils.to_tensor(target_raw, False)
    mask = utils.to_tensor(mask_raw, False)

    # Train model
    utils.fit(weights1, biases1, weights2, biases2, target, mask)

    return {
        "weights1": weights1.tolist(),
        "biases1": biases1.tolist(),
        "weights2": weights2.tolist(),
        "biases2": biases2.tolist(),
    }
