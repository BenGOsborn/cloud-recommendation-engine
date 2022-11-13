from typing import List
import torch


LEARNING_RATE = 0.007
EPOCHS = 1000
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
def loss_fn(predicted, actual, mask):
    mse = (predicted - actual) ** 2
    to_remove = mask * mse
    mse = mse - to_remove

    return torch.mean(mse)


# Convert from list to tensor
def to_tensor(raw_tensor: List, grad: bool):
    return torch.tensor(raw_tensor, dtype=torch.float32, requires_grad=grad)


# Train the params using minibatch gradient descent
def fit(weights1: torch.Tensor, biases1: torch.Tensor, weights2: torch.Tensor, biases2: torch.Tensor, target: torch.Tensor, mask: torch.Tensor):
    optimizer = torch.optim.Adam(
        [weights1, biases1, weights2, biases2],
        lr=LEARNING_RATE
    )

    # **** Hold on, these minibatches are wrong - we need to consider them quadratically, now just linearly like we currently have e.g.
    # we need to break it down so we have (u1, (s1, s2, ... sn)), (u2, (s1, s2, ... sn) ...)

    for _ in range(EPOCHS):
        for i in range(((len(weights1) - 1) // BATCH_SIZE) + 1):
            batch = (
                weights1[i:i + BATCH_SIZE, ...],
                biases1[i:i + BATCH_SIZE, ...],
                weights2[i:i + BATCH_SIZE, ...],
                biases2[i:i + BATCH_SIZE, ...],
                target[i:i + BATCH_SIZE, ...],
                mask[i:i + BATCH_SIZE, ...],
            )

            for elem in batch:
                print(elem.shape)
            print()

            prediction = model(*batch[:-2])

            l = loss_fn(prediction, *batch[-2:])

            l.backward()

            optimizer.step()
            optimizer.zero_grad()


if __name__ == "__main__":
    users_temp_batch_size = 8
    shows_temp_batch_size = 4

    weights1 = to_tensor([[1, 0]] * users_temp_batch_size, True)
    biases1 = to_tensor([1] * users_temp_batch_size, True)
    weights2 = to_tensor([[0, 1]] * shows_temp_batch_size, True)
    biases2 = to_tensor([1] * shows_temp_batch_size, True)

    target = to_tensor(
        [[1] * shows_temp_batch_size] * users_temp_batch_size,
        False
    )
    mask = to_tensor(
        [[0] * shows_temp_batch_size] * users_temp_batch_size,
        False
    )

    new_params = fit(weights1, biases1, weights2, biases2, target, mask)

    print(model(weights1, biases1, weights2, biases2))
