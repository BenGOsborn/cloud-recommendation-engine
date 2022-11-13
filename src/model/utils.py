from typing import List
import torch


LEARNING_RATE = 0.007
EPOCHS = 1000


class MatrixFactorization(torch.nn.Module):
    def __init__(self):
        super().__init__()

    # Weights = x * y * 1, Biases = x * 1 * 1
    def forward(self, weights1, biases1, weights2, biases2):
        # **** Looks like we might now have to pop another dimension onto this to get the multiplication to work

        weights1 = torch.transpose(weights1, 1, 2)
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
    torch.reshape(weights1_tensor, (len(weights1), -1, 1))

    weights2_tensor = torch.tensor(
        weights2,
        dtype=torch.float32,
        requires_grad=True
    )
    torch.reshape(weights2_tensor, (len(weights2), -1, 1))

    biases1_tensor = torch.tensor(
        biases1,
        dtype=torch.float32,
        requires_grad=True
    )
    torch.reshape(biases1_tensor, (len(biases1), 1, 1))

    biases2_tensor = torch.tensor(
        biases2,
        dtype=torch.float32,
        requires_grad=True
    )
    torch.reshape(biases2_tensor, (len(biases2), 1, 1))

    return weights1_tensor, biases1_tensor, weights2_tensor, biases2_tensor
