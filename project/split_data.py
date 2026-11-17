import os
import shutil
import numpy as np
from PIL import Image

SYMBOLS = ["R", "S", "C", "E", "H", "X", "9", "K", "7", "2"]
INPUT_DIR = "data/processed"
OUTPUT_DIR = "data/split"
TRAIN_PER_CLASS = 8          # 8 z 10 = 80 %
SEED = 42


def image_to_vector(path):
    pixels = np.array(Image.open(path).convert("L"))   # (28, 28), 0..255
    x = 1 - pixels / 255.0                             # písmo ≈ 1, pozadie ≈ 0
    return x.flatten()                                 # (784,)


def one_hot(index, num_classes=10):
    y = np.zeros(num_classes)
    y[index] = 1
    return y


rng = np.random.default_rng(SEED)   #SEED 42
X_train, Y_train, X_test, Y_test = [], [], [], []

for class_idx, symbol in enumerate(SYMBOLS):
    files = sorted(os.listdir(f"{INPUT_DIR}/{symbol}"))   # R_01.png … R_10.png
    order = rng.permutation(len(files))

    os.makedirs(f"{OUTPUT_DIR}/train/{symbol}", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/test/{symbol}", exist_ok=True)

    for pos, file_idx in enumerate(order):
        name = files[file_idx]
        path = f"{INPUT_DIR}/{symbol}/{name}"
        x = image_to_vector(path)
        y = one_hot(class_idx)

        if pos < TRAIN_PER_CLASS:                       # train
            X_train.append(x); Y_train.append(y)
            shutil.copy(path, f"{OUTPUT_DIR}/train/{symbol}/{name}")
        else:                                           # test
            X_test.append(x); Y_test.append(y)
            shutil.copy(path, f"{OUTPUT_DIR}/test/{symbol}/{name}")

X_train, Y_train = np.array(X_train), np.array(Y_train)
X_test, Y_test = np.array(X_test), np.array(Y_test)

np.save(f"{OUTPUT_DIR}/X_train.npy", X_train)
np.save(f"{OUTPUT_DIR}/Y_train.npy", Y_train)
np.save(f"{OUTPUT_DIR}/X_test.npy", X_test)
np.save(f"{OUTPUT_DIR}/Y_test.npy", Y_test)

print("shapes:", X_train.shape, Y_train.shape, X_test.shape, Y_test.shape)
print("value range:", X_train.min(), "to", X_train.max())
print("test samples per class:", Y_test.sum(axis=0))
