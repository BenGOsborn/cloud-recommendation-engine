import torch


class MatrixFactorization(torch.nn.Module):
    def __init__(self, weights1, biases1, weights2, biases2):
        super().__init__()

        # **** Remember, it will have to do multiple of the weights and biases at the same time - make sure it can compensate for this (that is one weights tensor = multiple users / shows)

        self.weights1 = weights1
        self.biases1 = biases1

        self.weights2 = weights2
        self.biases2 = biases2

    def forward(self):
        pass
