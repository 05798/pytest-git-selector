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
    shutil.copytree(os.path.join(this_dir, "resources", "sample_project_1"), dest, dirs_exist_ok=True)
    repo = git.Repo(dest)
    repo.git.add(".")
    repo.git.commit("-m", "Initial commit")
    return dest


def test_single_modified_file(sample_project_1):
    repo = git.Repo(sample_project_1)
    with open(os.path.join(sample_project_1, "sample_project_1", "f.py"), "a+") as f:
        f.write("\n# a comment")
    repo.git.add(".")
    repo.git.commit("-m", "A commit")

    test_files = select_test_files(
        ["HEAD~1..."], 
        [os.path.join(sample_project_1, "test/")], 
        [os.path.join(sample_project_1)], 
        dir_name=sample_project_1
    )

    assert test_files == set(
        (
            os.path.join(sample_project_1, "test", "test_f.py"), 
            os.path.join(sample_project_1, "test", "test_g.py")
        )
    )


def test_single_modified_file_2(sample_project_1):
    repo = git.Repo(sample_project_1)
    with open(os.path.join(sample_project_1, "sample_project_1", "g.py"), "a+") as f:
        f.write("\n# a comment")
    repo.git.add(".")
    repo.git.commit("-m", "A commit")

    test_files = select_test_files(
        ["HEAD~1..."], 
        [os.path.join(sample_project_1, "test/")], 
        [os.path.join(sample_project_1)], 
        dir_name=sample_project_1
    )

    assert test_files == set(
        (
            os.path.join(sample_project_1, "test", "test_g.py"),
        )
    )


def test_single_deleted_file(sample_project_1):
    repo = git.Repo(sample_project_1)
    os.remove(os.path.join(sample_project_1, "sample_project_1", "f.py"))
    repo.git.add(".")
    repo.git.commit("-m", "A commit")

    test_files = select_test_files(
        ["HEAD~1..."], 
        [os.path.join(sample_project_1, "test/")], 
        [os.path.join(sample_project_1)], 
        dir_name=sample_project_1
    )

    assert test_files == set(
        (
            os.path.join(sample_project_1, "test", "test_f.py"), 
            os.path.join(sample_project_1, "test", "test_g.py")
        )
    )
