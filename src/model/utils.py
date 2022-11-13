from typing import List
import torch


LEARNING_RATE = 0.007
EPOCHS = 1000


class MatrixFactorization(torch.nn.Module):
    def __init__(self):
        super().__init__()

    # Users = weights1 + biases1, Shows = weights2 + biases2
    # Weights1 = n * k, Biases1 = n * 1, Weights2 = m * k, Biases2 = m * 1 (n = amount of users, k = latent vector size, m = number of shows)
    def forward(self, weights1: torch.Tensor, biases1: torch.Tensor, weights2: torch.Tensor, biases2: torch.Tensor):
        weights2 = torch.transpose(weights2, 0, 1)
        biases1 = biases1.unsqueeze(0).transpose(0, 1)

        print(weights1)
        print(weights2)

        print(biases1)
        print(biases2)

        pred = torch.matmul(weights1, weights2)
        pred = pred + biases1 + biases2

        return torch.relu(pred)


model = MatrixFactorization()
loss_fn = torch.nn.MSELoss()


# Transform input weights and biases to Pytorch tensors
def transform_data(weights1: List[List[float]], biases1: List[List[float]], weights2: List[List[float]], biases2: List[List[float]]):
    weights1_tensor = torch.tensor(
        weights1,
        dtype=torch.float32,
        requires_grad=True
    )

    weights2_tensor = torch.tensor(
        weights2,
        dtype=torch.float32,
        requires_grad=True
    )

    biases1_tensor = torch.tensor(
        biases1,
        dtype=torch.float32,
        requires_grad=True
    )

    biases2_tensor = torch.tensor(
        biases2,
        dtype=torch.float32,
        requires_grad=True
    )

    return weights1_tensor, biases1_tensor, weights2_tensor, biases2_tensor
