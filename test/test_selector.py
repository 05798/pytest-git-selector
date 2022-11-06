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
        yield temp_dir


@pytest.fixture
def sample_project_1(empty_git_repo):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    dest = empty_git_repo
    shutil.copytree(
        os.path.join(this_dir, "resources", "sample_project_1"),
        dest,
        dirs_exist_ok=True,
    )
    repo = git.Repo(dest)
    repo.git.add(".")
    repo.git.commit("-m", "Initial commit")
    return dest


def modify_f_sample_project_1(project_root_dir):
    repo = git.Repo(project_root_dir)
    with open(os.path.join(project_root_dir, "sample_project_1", "f.py"), "a+") as f:
        f.write("\n# a comment")
    repo.git.add(".")
    repo.git.commit("-m", "Modify f")


def modify_g_sample_project_1(project_root_dir):
    repo = git.Repo(project_root_dir)
    with open(os.path.join(project_root_dir, "sample_project_1", "g.py"), "a+") as f:
        f.write("\n# a comment")
    repo.git.add(".")
    repo.git.commit("-m", "Modify g")


def delete_f_sample_project_1(project_root_dir):
    repo = git.Repo(project_root_dir)
    os.remove(os.path.join(project_root_dir, "sample_project_1", "f.py"))
    repo.git.add(".")
    repo.git.commit("-m", "Delete f")


@pytest.mark.parametrize(
    ("side_effect", "expected"), 
    [
        (modify_f_sample_project_1, {"test/test_f.py", "test/test_g.py"}), 
        (modify_g_sample_project_1, {"test/test_g.py"}), 
        (delete_f_sample_project_1, {"test/test_f.py", "test/test_g.py"})
    ]
)
def test_single_commit_change(sample_project_1, side_effect, expected):
    side_effect(sample_project_1)

    test_files = select_test_files(
        ["HEAD~1..."],
        [os.path.join(sample_project_1, "test/")],
        [os.path.join(sample_project_1)],
        dir_name=sample_project_1,
    )

    # Expected must be in absolute paths
    expected = set(os.path.join(sample_project_1, p) for p in expected)

    assert test_files == expected
