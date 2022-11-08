from small_project_b.h import divide, modulo


def test_divide():
    assert divide(20, 5) == 4


def test_modulo():
    with open("test_h_modulo_inputs.csv", "r") as f:
        x, y, z = map(int, f.read().split(","))
        assert modulo(x, y) == z
