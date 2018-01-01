import sys, os
sys.path.append(os.pardir)
import numpy as np
import datetime
import pickle
from lib.MNIST import MNIST
from lib.layers import DenseLayer, SigmoidLayer, SoftmaxCrossEntropyLayer
from collections import OrderedDict

class FastBasicNet:
    def __init__(self):
        self.params = None
        self.layers = None

        self.init_params()
        self.init_layers()

    def init_params(self):
        SIGMA = 0.01

        self.params = {}
        self.params['W1'] = np.random.randn(28*28, 32) * SIGMA
        self.params['b1'] = np.random.rand(32) * SIGMA
        self.params['W2'] = np.random.randn(32, 10) * SIGMA
        self.params['b2'] = np.random.rand(10) * SIGMA

    def init_layers(self):
        self.layers = OrderedDict()
        self.layers['Dense1'] = DenseLayer(self.params['W1'], self.params['b1'])
        self.layers['Sigmoid1'] = SigmoidLayer()
        self.layers['Dense2'] = DenseLayer(self.params['W2'], self.params['b2'])
        self.last_layer = SoftmaxCrossEntropyLayer()

    def save_params(self, filename):
        pickle.dump(self.params, open(filename, "wb"))
        print("Saved params at {}".format(filename))

    def load_params(self, filename):
        self.params = pickle.load(open(filename, "rb"))
        print("Loaded params from {}".format(filename))
        self.init_layers()
        print("Recreated layers with the params")

    def predict(self, X):
        out = X
        for layer in self.layers.values():
            out = layer.forward(out)
        return out

    def loss(self, X, T):
        Z = self.predict(X)
        loss = self.last_layer.forward(Z, T)
        return loss

    def accuracy(self, X, T):
        Z = self.predict(X)
        Z_index = np.argmax(Z, axis=1)
        T_index = np.argmax(T, axis=1)
        return np.mean(Z_index == T_index)

    def train(self, train_images, train_labels, test_images, test_labels, epochs=5):
        train_size = train_images.shape[0]
        batch_size = 100
        iteration_per_epoch = train_size // batch_size
        total_iterations = iteration_per_epoch * epochs

        itr = 0
        for epoch in range(epochs):
            print("========== Epoch {} ==========".format(epoch))

            for _ in range(iteration_per_epoch):
                if itr % 100 == 0:
                    print("Iteration {}/{}: {}".format(itr, total_iterations, datetime.datetime.now()))

                if itr % 300 == 0:
                    train_loss = self.loss(train_images, train_labels)
                    test_loss = self.loss(test_images, test_labels)
                    print("Losses in Iteration {}: train: {}, test: {}".format(itr, train_loss, test_loss))

                if itr % 300 == 0:
                    train_acc = self.accuracy(train_images, train_labels)
                    test_acc = self.accuracy(test_images, test_labels)
                    print("Accuracy in Iteration {}: train: {}, test: {}".format(itr, train_acc, test_acc))

                # if itr % 100 == 0:
                #     pickle_filename = "params_epoch_{}_itr_{}.pkl".format(epoch, itr)
                #     self.save_params(pickle_filename)

                batch_mask = np.random.choice(train_size, batch_size)
                batch_images = train_images[batch_mask]
                batch_labels = train_labels[batch_mask]
                self.gradient_descent(batch_images, batch_labels)

                itr += 1

    def gradient_descent(self, X, T):
        ETA = 0.1
        grads = fast_basic_net.gradients(X, T)
        for param_name in ['W1', 'b1', 'W2', 'b2']:
            self.params[param_name] -= ETA * grads[param_name]

    def gradients(self, X, T):
        self.loss(X, T)

        dL = self.last_layer.backward()
        layers = list(self.layers.values())
        layers.reverse()
        for layer in layers:
            dL = layer.backward(dL)

        gradients = {}
        gradients['W1'] = self.layers['Dense1'].dW
        gradients['b1'] = self.layers['Dense1'].db
        gradients['W2'] = self.layers['Dense2'].dW
        gradients['b2'] = self.layers['Dense2'].db

        return gradients

    def numerical_gradients(self, X, T):
        loss = lambda: self.loss(X, T)

        gradients = {}
        for param_name in ['W1', 'b1', 'W2', 'b2']:
            gradients[param_name] = self.numerical_gradient(loss, self.params[param_name])

        return gradients

    def numerical_gradient(self, loss, variables):
        h = 1e-4
        gradients = np.zeros_like(variables)

        itr = np.nditer(variables, flags=['multi_index'], op_flags=['readwrite'])
        while not itr.finished:
            original = itr[0].copy()

            itr[0] = original + h
            # print("original + h: {}".format(itr[0]))
            v1 = loss()
            itr[0] = original - h
            # print("original - h: {}".format(itr[0]))
            v2 = loss()
            gradients[itr.multi_index] = (v1 - v2) / (2 * h)
            # print("grad: {}".format(gradients[itr.multi_index]))

            itr[0] = original
            itr.iternext()

        return gradients

    def gradient_check(self, images, labels):
        print("Checking gradients...")
        THRESHOLD = 1e-5
        backprop_grad = self.gradients(images, labels)
        numerical_grad = self.numerical_gradients(images, labels)

        for key in backprop_grad.keys():
            b = backprop_grad[key].reshape(-1)
            n = numerical_grad[key].reshape(-1)

            diff = np.linalg.norm(b - n)
            prop = np.linalg.norm(b) + np.linalg.norm(n)
            check = diff / prop
            if check < THRESHOLD:
                result = 'OK'
            else:
                result = 'NG'

            print("gradient {}: {} ({})".format(key, result, check))


if __name__ == '__main__':
    print("this is main")
    fast_basic_net = FastBasicNet()

    mnist = MNIST()
    train_images, train_labels, test_images, test_labels = mnist.get_dataset()

    # batch_images = train_images[:20]
    # batch_labels = train_labels[:20]

    fast_basic_net.train(train_images, train_labels, test_images, test_labels, epochs=5)
    print("Done!")

    # fast_basic_net.load_params('params_after_5_epochs.pkl')

    # fast_basic_net.accuracy(batch_images, batch_labels)

    # acc = fast_basic_net.accuracy(test_images, test_labels)
    # print(acc)

    train_loss = fast_basic_net.loss(train_images, train_labels)
    test_loss = fast_basic_net.loss(test_images, test_labels)
    print("[Losses] train: {}, test: {}".format(train_loss, test_loss))

    train_acc = fast_basic_net.accuracy(train_images, train_labels)
    test_acc = fast_basic_net.accuracy(test_images, test_labels)
    print("[Accuracy] train: {}, test: {}".format(train_acc, test_acc))

    fast_basic_net.save_params("params_6_epoch.pkl")
