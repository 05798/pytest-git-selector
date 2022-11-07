import git
import os
import pytest
import shutil
import tempfile

from pytest_git_selector.selector import select_test_files


@pytest.fixture
def empty_git_repo():
    with tempfile.TemporaryDirectory() as temp_dir:
        g = git.cmd.Git(temp_dir)
        g.init()
        g.config("--local", "user.name", "test")
        g.config("--local", "user.email", "test@email.com")
        yield temp_dir


@pytest.fixture
def small_project_a(empty_git_repo):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    dest = empty_git_repo
    shutil.copytree(
        os.path.join(this_dir, "resources", "small_project_a"),
        dest,
        dirs_exist_ok=True,
    )
    repo = git.Repo(dest)
    repo.git.add(".")
    repo.git.commit("-m", "Initial commit")
    return dest


def modify_f_small_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    with open(os.path.join(project_root_dir, "small_project_a", "f.py"), "a+") as f:
        f.write("# a comment\n")
    repo.git.add(".")
    repo.git.commit("-m", "Modify f")


def modify_g_small_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    with open(os.path.join(project_root_dir, "small_project_a", "g.py"), "a+") as f:
        f.write("# a comment\n")
    repo.git.add(".")
    repo.git.commit("-m", "Modify g")


def delete_f_small_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    os.remove(os.path.join(project_root_dir, "small_project_a", "f.py"))
    repo.git.add(".")
    repo.git.commit("-m", "Delete f")


def add_h_small_project_a(project_root_dir):
    repo = git.Repo(project_root_dir)
    with open(os.path.join(project_root_dir, "small_project_a", "h.py"), "w+") as h:
        h.write("pass\n")
    with open(os.path.join(project_root_dir, "test", "test_h.py"), "w+") as h:
        h.write("import small_project_a.h\n")
    with open(os.path.join(project_root_dir, "small_project_a", "g.py"), "a+") as g:
        g.write("import small_project_a.h")
    repo.git.add(".")
    repo.git.commit("-m", "Add h. Import h from g")


@pytest.mark.parametrize(
    ("repo", "side_effect", "git_diff_args", "test_paths", "python_paths", "expected"),
    [
        ("small_project_a", modify_f_small_project_a, ["HEAD~1..."], ["test"], ["."], {"test/test_f.py", "test/test_g.py"}),
        ("small_project_a", modify_g_small_project_a, ["HEAD~1..."], ["test"], ["."], {"test/test_g.py"}),
        ("small_project_a", delete_f_small_project_a, ["HEAD~1..."], ["test"], ["."], {"test/test_f.py", "test/test_g.py"}),
        ("small_project_a", add_h_small_project_a, ["HEAD~1..."], ["test"], ["."], {"test/test_g.py", "test/test_h.py"}),
    ],
)
def test_select_test_files(repo, side_effect, git_diff_args, test_paths, python_paths, expected, request):
    repo_path = request.getfixturevalue(repo)
    side_effect(repo_path)

    test_files = select_test_files(
        git_diff_args,
        [os.path.join(repo_path, p) for p in test_paths],
        [os.path.join(repo_path, p) for p in python_paths],
        dir_name=repo_path,
    )

    # Expected must be in absolute paths
    expected = set(os.path.join(repo_path, p) for p in expected)

    assert test_files == expected
