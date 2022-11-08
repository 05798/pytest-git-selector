import git
import os
import pytest
import shutil
import tempfile

pytest_plugins = ["pytester"]


@pytest.fixture
def empty_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def empty_git_repo(empty_repo):
    g = git.cmd.Git(empty_repo)
    g.init()
    g.config("--local", "user.name", "test")
    g.config("--local", "user.email", "test@email.com")
    return empty_repo


def initialize_resource_repo(dest, resource_repo):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    shutil.copytree(
        os.path.join(this_dir, "resources", resource_repo),
        dest,
        dirs_exist_ok=True,
    )
    repo = git.Repo(dest)
    repo.git.add(".")
    repo.git.commit("-m", "Initial commit")
    return dest


@pytest.fixture
def small_project_a(empty_git_repo):
    """
    Create a project with the following dependencies:

    f/f.py -> g/g.py

    ┌──────┐
    │f/f.py│
    └┬─────┘
    ┌▽─────┐
    │g/g.py│
    └──────┘

    """
    return initialize_resource_repo(empty_git_repo, "small_project_a")


@pytest.fixture
def medium_project_a(empty_git_repo):
    """
    Creates a project with the following dependencies:

    src/a/a_3.py -> src/a/a_1.py
    src/a/a_3.py -> src/a/a_2.py
    src/a/a_3.py -> src/b/b_1.py
    src/c/c_1.py -> src/a/a_3.py
    src/c/c_1.py -> src/b/b_1.py
    src/c/c_2.py -> src/a/a_2.py
    src/d/d_1.py -> src/c/c_1.py
    src/d/d_1.py -> src/b/b_2.py
    src/d/d_1.py -> src/c/c_2.py

    ┌───────────────────────────────────┐           
    │src/d/d_1.py                       │           
    └┬─────────────┬───────────────────┬┘           
    ┌▽───────────┐┌▽─────────────────┐┌▽───────────┐
    │src/c/c_2.py││src/c/c_1.py      ││src/b/b_2.py│
    └┬───────────┘└┬────────────────┬┘└────────────┘
    │┌────────────▽───────────────┐│               
    ││src/a/a_3.py                ││               
    │└┬───────────┬─────────────┬─┘│               
    ┌▽─▽─────────┐┌▽───────────┐┌▽──▽────────┐      
    │src/a/a_2.py││src/a/a_1.py││src/b/b_1.py│      
    └────────────┘└────────────┘└────────────┘      
    
    """

    return initialize_resource_repo(empty_git_repo, "medium_project_a")


def modify_f_small_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    with open(os.path.join(project_root_dir, "small_project_a", "f.py"), "a+") as f:
        f.write("# modify_f_small_project_a\n")
    repo.git.add(".")
    repo.git.commit("-m", "Modify f.py")


def rename_f_small_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    os.rename(
        os.path.join(project_root_dir, "small_project_a", "f.py"),
        os.path.join(project_root_dir, "small_project_a", "f_2.py"),
    )
    repo.git.add(".")
    repo.git.commit("-m", "Rename f.py to f_2.py")


def modify_g_small_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    with open(os.path.join(project_root_dir, "small_project_a", "g.py"), "a+") as f:
        f.write("# modify_g_small_project_a\n")
    repo.git.add(".")
    repo.git.commit("-m", "Modify g.py")


def delete_f_small_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    os.remove(os.path.join(project_root_dir, "small_project_a", "f.py"))
    repo.git.add(".")
    repo.git.commit("-m", "Delete f.py")


def add_h_small_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    repo.git.checkout(
        "-b", "base"
    )  # So we don't have to deduce whether it is main/master branch
    repo.git.checkout("-b", "feature")
    with open(os.path.join(project_root_dir, "small_project_a", "h.py"), "w+") as h:
        h.write("pass\n")
    repo.git.add(".")
    repo.git.commit("-m", "Add h.py")

    with open(os.path.join(project_root_dir, "test", "test_h.py"), "w+") as h:
        h.write("import small_project_a.h\n")
    repo.git.add(".")
    repo.git.commit("-m", "Add test_h.py")

    with open(os.path.join(project_root_dir, "small_project_a", "g.py"), "a+") as g:
        g.write("import small_project_a.h")
    repo.git.add(".")
    repo.git.commit("-m", "Import h.py from g.py")


def modify_b_1_medium_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)

    with open(os.path.join(project_root_dir, "src", "b", "b_1.py"), "a+") as b_1:
        b_1.write("# modify_b_1_medium_project_a\n")

    repo.git.add(".")
    repo.git.commit("-m", "Modify b_1.py")


def b_2_depends_on_a_2_medium_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)

    with open(os.path.join(project_root_dir, "src", "b", "b_2.py"), "a+") as b_2:
        b_2.write("import a.a_2\n")

    repo.git.add(".")
    repo.git.commit("-m", "Make b_2.py depend on a_2.py")

    with open(os.path.join(project_root_dir, "src", "a", "a_2.py"), "a+") as a_2:
        a_2.write("# b_2_depends_on_a_2_medium_project_a\n")

    repo.git.add(".")
    repo.git.commit("-m", "Modify a_2.py")


def complex_workflow_a_medium_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    repo.git.checkout(
        "-b", "base"
    )  # So we don't have to deduce whether it is main/master branch
    repo.git.checkout("-b", "feature-1")

    with open(os.path.join(project_root_dir, "src", "a", "a_1.py"), "a+") as a_1:
        a_1.write("# a_1.py complex_workflow_a_medium_project_a\n")

    repo.git.add(".")
    repo.git.commit("-m", "Modify a_1.py")

    repo.git.checkout("-b", "feature-2")
    repo.git.checkout("feature-1")

    with open(os.path.join(project_root_dir, "src", "b", "b_2.py"), "a+") as b_2:
        b_2.write("# b_2.py complex_workflow_a_medium_project_a\n")

    repo.git.add(".")
    repo.git.commit("-m", "Modify b_2.py")

    repo.git.checkout("feature-2")

    with open(os.path.join(project_root_dir, "src", "b", "b_1.py"), "a+") as b_1:
        b_1.write("# b_1.py complex_workflow_a_medium_project_a\n")

    repo.git.add(".")
    repo.git.commit("-m", "Modify b_1.py")

    os.remove(os.path.join(project_root_dir, "src", "a", "a_2.py"))

    repo.git.add(".")
    repo.git.commit("-m", "Delete a_2.py")


def complex_workflow_a_medium_project_a_feature_1(project_root_dir):
    complex_workflow_a_medium_project_a(project_root_dir)
    git.Repo(project_root_dir).git.checkout("feature-1")


def complex_workflow_b_medium_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    repo.git.checkout(
        "-b", "base"
    )  # So we don't have to deduce whether it is main/master branch
    repo.git.checkout("-b", "feature-1")

    os.rename(
        os.path.join(project_root_dir, "src", "b", "b_1.py"),
        os.path.join(project_root_dir, "src", "b", "b_1a.py"),
    )

    repo.git.add(".")
    repo.git.commit("-m", "Rename b_1.py to b_1a.py")

    repo.git.checkout("-b", "feature-2")
    repo.git.checkout("feature-1")

    with open(os.path.join(project_root_dir, "src", "c", "c_2.py"), "a+") as c_2:
        c_2.write("# c_2.py complex_workflow_b_medium_project_a\n")

    repo.git.add(".")
    repo.git.commit("-m", "Modify c_2.py")

    os.rename(
        os.path.join(project_root_dir, "src", "a", "a_2.py"),
        os.path.join(project_root_dir, "src", "a", "a_2a.py"),
    )

    repo.git.add(".")
    repo.git.commit("-m", "Rename a_2.py to a_2a.py")

    repo.git.checkout("feature-2")

    os.remove(os.path.join(project_root_dir, "src", "a", "a_1.py"))

    repo.git.add(".")
    repo.git.commit("-m", "Delete a_1.py")


def complex_workflow_b_medium_project_a_feature_1(project_root_dir):
    complex_workflow_b_medium_project_a(project_root_dir)
    git.Repo(project_root_dir).git.checkout("feature-1")
