import torch


class MatrixFactorization(torch.nn.Module):
    def __init__(self, weights1, weights2):
        super().__init__()

        self.weights1 = weights1
        self.weights2 = weights2
