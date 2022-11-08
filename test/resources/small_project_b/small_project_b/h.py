from small_project_b.f.f_2 import multiply
from small_project_b.g import subtract


def divide(x, y):
    return multiply(x, 1 / y)


def modulo(x, y):

    while subtract(x, y) > 0:
        x = subtract(x, y)

    return x
