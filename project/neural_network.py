import numpy as np
import matplotlib.pyplot as plt


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size, seed=42):
        self.rng = np.random.default_rng(seed)

        # W1: (hidden_size x input_size), b1: (hidden_size)
        self.W1 = self.rng.normal(0, np.sqrt(1 / input_size), (hidden_size, input_size))
        self.b1 = np.zeros(hidden_size)

        # W2: (output_size x hidden_size), b2: (output_size)
        self.W2 = self.rng.normal(0, np.sqrt(1 / hidden_size), (output_size, hidden_size))
        self.b2 = np.zeros(output_size)


    def sigmoid(self, z):
        return 1 / (1 + np.exp(-z))

    def softmax(self, z):
        e = np.exp(z - np.max(z))     # numerická stabilita
        return e / np.sum(e)

    def forward(self, x):
        self.x = x                                  # odložíme si pre backward
        self.z1 = self.W1 @ x + self.b1             # (64,)
        self.h = self.sigmoid(self.z1)              # (64,)
        self.z2 = self.W2 @ self.h + self.b2        # (10,)
        self.y_hat = self.softmax(self.z2)          # (10,) pravdepodobnosti
        return self.y_hat
    

    def compute_loss(self, y_pred, y_true):
        eps = 1e-12
        return -np.sum(y_true * np.log(y_pred + eps))

    def backward(self, y, learning_rate):
        # výstupná vrstva
        delta2 = self.y_hat - y                         # (10,)
        dW2 = np.outer(delta2, self.h)                  # (10, 64)
        db2 = delta2                                    # (10,)

        # skrytá vrstva (používa STARÉ W2)
        delta1 = (self.W2.T @ delta2) * self.h * (1 - self.h)   # (64,)
        dW1 = np.outer(delta1, self.x)                  # (64, 784)
        db1 = delta1                                    # (64,)

        # gradientný zostup
        self.W2 -= learning_rate * dW2
        self.b2 -= learning_rate * db2
        self.W1 -= learning_rate * dW1
        self.b1 -= learning_rate * db1


    def train(self, X_train, Y_train, epochs, learning_rate):
        losses = []
        n = len(X_train)
        for epoch in range(epochs):
            order = self.rng.permutation(n)        # premiešanie pred každou epochou
            total_loss = 0.0
            for i in order:                        # SGD: po jednej vzorke
                y_pred = self.forward(X_train[i])
                total_loss += self.compute_loss(y_pred, Y_train[i])
                self.backward(Y_train[i], learning_rate)
            losses.append(total_loss / n)          # priemerná strata epochy
            if (epoch + 1) % 50 == 0 or epoch == 0:
                print(f"epoch {epoch + 1:3d}  loss {losses[-1]:.4f}")
        return losses

    def predict(self, X):
        return np.array([np.argmax(self.forward(x)) for x in X])


SYMBOLS = ["R", "S", "C", "E", "H", "X", "9", "K", "7", "2"]

X_train = np.load("data/split/X_train.npy")
Y_train = np.load("data/split/Y_train.npy")
X_test = np.load("data/split/X_test.npy")
Y_test = np.load("data/split/Y_test.npy")

input_size = 784
hidden_size = 128
output_size = 10

model = NeuralNetwork(input_size, hidden_size, output_size)
losses = model.train(X_train, Y_train, epochs=300, learning_rate=0.1)

# vyhodnotenie
train_pred = model.predict(X_train)
test_pred = model.predict(X_test)
train_true = np.argmax(Y_train, axis=1)       # z one-hot späť na číslo triedy
test_true = np.argmax(Y_test, axis=1)

train_acc = np.mean(train_pred == train_true)
test_acc = np.mean(test_pred == test_true)
print(f"\ntrain accuracy: {train_acc * 100:.1f} %")
print(f"test accuracy:  {test_acc * 100:.1f} %")

# ktoré testovacie obrázky sieť pomýlila
for p, t in zip(test_pred, test_true):
    mark = "OK" if p == t else "WRONG"
    print(f"  true {SYMBOLS[t]}  predicted {SYMBOLS[p]}  {mark}")

# graf straty
plt.plot(range(1, len(losses) + 1), losses)
plt.xlabel("epoch")
plt.ylabel("average cross-entropy loss")
plt.title(f"Training loss (784-{hidden_size}-10, lr=0.1)")
plt.yscale("log")
plt.grid(True)
plt.savefig("loss.png", dpi=150)
print("graph saved to loss.png")
