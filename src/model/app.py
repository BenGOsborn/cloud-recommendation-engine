import torch

torch.manual_seed(1234)


class MatrixFactorization(torch.nn.Module):
    def __init__(self):
        super().__init__()

    # Weights = n * x, Biases = n * 1
    def forward(self, weights1, biases1, weights2, biases2):
        pred = torch.dot(weights1, weights2) + biases1 + biases2

        return torch.relu(pred)


n = 1
x = 10

weights1 = torch.rand(n, x, requires_grad=True)
weights2 = torch.rand(n, x, requires_grad=True)

biases1 = torch.rand(n, 1, requires_grad=True)
biases2 = torch.rand(n, 1, requires_grad=True)

target = torch.tensor([[1]] * n)

print("Weights 1", weights1)
print("Biases 1", biases1)

print("Weights 2", weights2)
print("Biases 1", biases2)

print("Target", target)

model = MatrixFactorization()
