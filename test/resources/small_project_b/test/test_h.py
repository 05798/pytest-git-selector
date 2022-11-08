import os

from small_project_b.h import divide, modulo


def test_divide():
    assert divide(20, 5) == 4


def test_modulo():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "test_h_modulo_inputs.csv"), "r") as f:
        x, y, z = map(int, f.read().split(","))
        assert modulo(x, y) == z
