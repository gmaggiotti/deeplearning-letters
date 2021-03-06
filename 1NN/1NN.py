import numpy as np


def sigmoid(x, deriv=False):
    if (deriv == True):
        return x * (1 - x)
    return 1 / (1 + np.exp(-x))


def tanh(x, deriv=False):
    if (deriv == True):
        return 1 - np.power(x, 2)
    return np.tanh(x)  # (np.exp(x) - np.exp(-x))/(np.exp(x) + np.exp(-x))


def softplus(x, deriv=False):
    if (deriv == True):
        return 1 / (1 + np.exp(-x))
    return np.log(1 + np.exp(x))

def relu(x, deriv=False):
    if(deriv == True):
        return 1 * (x >= 0)
    return np.max(x,0)


# input data, each column represent a dif neuron
X = np.loadtxt("1NN/X.txt", delimiter=",")
max = np.matrix(X).max()
X = 2 * X / float(max) - 1
# output, are the one-hot encoded labels
y = np.loadtxt("1NN/Y.txt", delimiter=",").reshape(X.__len__(), 1)

np.random.seed(
    1)  # The seed for the random generator is set so that it will return the same random numbers each time,
# which is sometimes useful for debugging.

# Now we intialize the weights to random values. w0 is the weight between the input layer and the hidden layer.

# synapses
w0 = 2 * np.random.random((X.size / X.__len__(), 1)) - 1  # mxn matrix of weights

# This is the main training loop. The output shows the evolution of the error between the model and desired. The
# error steadily decreases.
for j in xrange(60000):

    # Calculate forward through the network.
    l1 = relu(np.dot(X, w0))

    # Error back propagation of errors using the chain rule.
    l1_error = y - l1
    if (j % 10000) == 0:  # Only print the error every 10000 steps, to save time and limit the amount of output.
        print("epoch {}: {}".format(j, np.mean(np.abs(l1_error))))

    adjustment = l1_error * relu(l1, deriv=True)  # (y-a).d/dw(-a), a = sigmoid(Sum Xi*Wi)

    # update weights (no learning rate term)
    w0 += X.T.dot(adjustment)


def predict(X1):
    max = np.matrix(X1).max()
    l0 = 2 * np.array(X1, dtype=np.float32) / float(max) - 1
    l1 = relu(np.dot(l0, w0))
    return l1[0]  # since process X1[0] output would be l2[0]


test_dataset = [1, 9, 19, 33, 16, 2, 1]
result = predict(test_dataset)
print("expected output 1, predicted output: " + repr(result))
assert (result > 0.95), "Test Failed. Expected result > 0.95"

test_dataset = [1, 0, 1, 4, 1, 3, 1]
result = predict(test_dataset)
print("expected output 0, predicted output " + repr(result))
assert (result < 0.95), "Test Failed. Expected result < 0.95"
