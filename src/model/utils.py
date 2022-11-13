from typing import List
import torch


LEARNING_RATE = 0.007
EPOCHS = 1000


class MatrixFactorization(torch.nn.Module):
    def __init__(self):
        super().__init__()

    # Weights = n * x, Biases = n * 1
    def forward(self, weights1, biases1, weights2, biases2):
        weights1 = torch.transpose(weights1, 1, 2)
        pred = torch.matmul(weights1, weights2)
        pred = pred + biases1 + biases2

        return torch.relu(pred)


model = MatrixFactorization()
loss_fn = torch.nn.MSELoss()


if __name__ == "__main__":
    x = 10
    y = 10

    weights1 = torch.rand(x, y, 1, requires_grad=True)
    weights2 = torch.rand(x, y, 1, requires_grad=True)

    biases1 = torch.rand(x, 1, 1, requires_grad=True)
    biases2 = torch.rand(x, 1, 1, requires_grad=True)

    target = torch.tensor([[1]] * x, dtype=torch.float32)

    print("Weights 1", weights1)
    print("Biases 1", biases1)

    print("Weights 2", weights2)
    print("Biases 2", biases2)

    print("Target", target)

    optimizer = torch.optim.Adam(
        [weights1, biases1, weights2, biases2],
        lr=LEARNING_RATE
    )

    for epoch in range(EPOCHS):
        prediction = model(weights1, biases1, weights2, biases2)

        l = loss_fn(prediction, target)

        l.backward()

        optimizer.step()
        optimizer.zero_grad()

    prediction = model(weights1, biases1, weights2, biases2)
    print("Prediction", prediction)

    print("NEW Weights 1", weights1)
    print("NEW Biases 1", biases1)

    print("NEW Weights 2", weights2)
    print("NEW Biases 2", biases2)


# Transform input weights and biases to Pytorch tensors
def transform_data(weights1: List[List[float]], biases1: List[List[float]], weights2: List[List[float]], biases2: List[List[float]]):
    weights1_tensor = torch.tensor(weights1, requires_grad=True)
    torch.reshape(weights1_tensor, (len(weights1), -1, 1))

    weights2_tensor = torch.tensor(weights2, requires_grad=True)
    torch.reshape(weights2_tensor, (len(weights2), -1, 1))

    biases1_tensor = torch.tensor(biases1, requires_grad=True)
    torch.reshape(biases1_tensor, (len(biases1), 1, 1))

    biases2_tensor = torch.tensor(biases2, requires_grad=True)
    torch.reshape(biases2_tensor, (len(biases2), 1, 1))

    return weights1_tensor, biases1_tensor, weights2_tensor, biases2_tensor
