from typing import List
import torch


LEARNING_RATE = 0.007
EPOCHS = 50
BATCH_SIZE = 4


class MatrixFactorization(torch.nn.Module):
    def __init__(self):
        super().__init__()

    # Users = weights1 + biases1, Shows = weights2 + biases2
    # Weights1 = n * k, Biases1 = n * 1, Weights2 = m * k, Biases2 = m * 1 (n = amount of users, k = latent vector size, m = number of shows)
    # Output = n * m
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
# predicted.shape == actual.shape == mask.shape
def loss_fn(predicted, actual, mask):
    mse = (predicted - actual) ** 2
    to_remove = mask * mse
    mse = mse - to_remove

    return torch.mean(mse)


# Convert from list to tensor
def to_tensor(raw_tensor: List, grad: bool):
    return torch.tensor(raw_tensor, dtype=torch.float32, requires_grad=grad)


# Train the params using gradient descent
def fit(weights1: torch.Tensor, biases1: torch.Tensor, weights2: torch.Tensor, biases2: torch.Tensor, target: torch.Tensor, mask: torch.Tensor):
    optimizer = torch.optim.Adam(
        [weights1, biases1, weights2, biases2],
        lr=LEARNING_RATE
    )

    for _ in range(EPOCHS):
        prediction = model(weights1, biases1, weights2, biases2)

        l = loss_fn(prediction, target, mask)

        l.backward()

        optimizer.step()
        optimizer.zero_grad()
