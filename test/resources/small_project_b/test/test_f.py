import small_project_b.f.f_1
import small_project_b.f.f_2


def test_add():
    assert small_project_b.f.f_1.add(1, 1) == 2


def test_multiply():
    assert small_project_b.f.f_2.multiply(2, 2) == 4


def test_hello_world():
    assert small_project_b.f.f_1.hello_world() == "Hello world!"
