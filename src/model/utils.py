from typing import List
import torch


LEARNING_RATE = 0.007
EPOCHS = 1000
BATCH_SIZE = 16


class MatrixFactorization(torch.nn.Module):
    def __init__(self):
        super().__init__()

    # Users = weights1 + biases1, Shows = weights2 + biases2
    # Weights1 = n * k, Biases1 = n * 1, Weights2 = m * k, Biases2 = m * 1 (n = amount of users, k = latent vector size, m = number of shows)
    def forward(self, weights1: torch.Tensor, biases1: torch.Tensor, weights2: torch.Tensor, biases2: torch.Tensor):
        # Apply all shows to every user
        weights2 = torch.transpose(weights2, 0, 1)
        # Apply user biases vertically
        biases1 = biases1.unsqueeze(0).transpose(0, 1)

        pred = torch.matmul(weights1, weights2)
        pred = pred + biases1 + biases2

        return torch.relu(pred)


model = MatrixFactorization()


# Mean squared error loss with masking - mask is binary matrix where 0 means keep and 1 means ignore
def loss_fn(predicted, actual, mask):
    mse = (predicted - actual) ** 2
    to_remove = mask * mse
    mse = mse - to_remove

    return torch.mean(mse)


# Convert from list to tensor
def to_tensor(raw_tensor: List, grad: bool):
    return torch.tensor(raw_tensor, dtype=torch.float32, requires_grad=grad)


# Train the params
def fit(weights1: torch.Tensor, biases1: torch.Tensor, weights2: torch.Tensor, biases2: torch.Tensor, target: torch.Tensor, mask: torch.Tensor):
    optimizer = torch.optim.Adam(
        [weights1, biases1, weights2, biases2],
        lr=LEARNING_RATE
    )

    # Create batches
    weights1 = torch.split(weights1, BATCH_SIZE)
    biases1 = torch.split(biases1, BATCH_SIZE)
    weights2 = torch.split(weights2, BATCH_SIZE)
    biases2 = torch.split(biases2, BATCH_SIZE)
    target = torch.split(target, BATCH_SIZE)
    mask = torch.split(mask, BATCH_SIZE)

    for _ in range(EPOCHS):
        for i in range(weights1(len)):
            batch = (
                weights1[i],
                biases1[i],
                weights2[i],
                biases2[i],
                target[i],
                mask[i],
            )

            prediction = model(*batch[:-2])

            l = loss_fn(prediction, *batch[-2:])

            l.backward()

            optimizer.step()
            optimizer.zero_grad()


if __name__ == "__main__":
    weights1 = to_tensor([[1, 0]], True)
    biases1 = to_tensor([1], True)
    weights2 = to_tensor([[0, 1]], True)
    biases2 = to_tensor([1], True)

    target = [1]
    mask = [0]

    print(weights1, biases1, weights2, biases2)

    fit(weights1, biases1, weights2, biases2, target, mask)

    print(weights1, biases1, weights2, biases2)
