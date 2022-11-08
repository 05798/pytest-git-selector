import os


def add(x, y):
    return x + y


def hello_world():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "f_1.txt"), "r") as f:
        return f.readlines().strip()
