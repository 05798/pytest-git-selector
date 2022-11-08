import contextlib
import io
import os
import pytest
import pytest_git_selector.cmd
import sys

from conftest import (
    complex_workflow_a_medium_project_a,
    modify_f_small_project_a,
    modify_f_1_txt_small_project_b,
)


# To run these tests, you will need to install the package in editable mode so that subprocess can use the entry point
@pytest.mark.parametrize(
    (
        "repo",
        "side_effect",
        "dir_",
        "test_path",
        "src_path",
        "extra_deps_file",
        "git_diff_args",
        "expected",
    ),
    [
        (
            "small_project_a",
            modify_f_small_project_a,
            ".",
            ["test"],
            ["."],
            None,
            ["HEAD~1..."],
            {"test/test_f.py", "test/test_g.py"},
        ),
        (
            "small_project_a",
            modify_f_small_project_a,
            ".",
            ["test"],
            ["."],
            None,
            ["HEAD~1...", "--diff-filter=m"],
            set(),
        ),
        (
            "small_project_b",
            modify_f_1_txt_small_project_b,
            ".",
            ["test"],
            ["."],
            "extra_deps.txt",
            ["HEAD~1..."],
            {"test/test_f.py", "test/test_g.py", "test/test_h.py"},
        ),
        (
            "medium_project_a",
            complex_workflow_a_medium_project_a,
            ".",
            ["test"],
            ["src"],
            None,
            ["base..."],
            {
                "test/test_a/test_a_1.py",
                "test/test_a/test_a_2.py",
                "test/test_a/test_a_3.py",
                "test/test_b/test_b_1.py",
                "test/test_b/test_b.py",
                "test/test_c/test_c_1.py",
                "test/test_c/test_c_2.py",
                "test/test_d/test_d_1.py",
            },
        ),
        (
            "small_project_a",
            modify_f_small_project_a,
            ".",
            ["fake"],
            ["fake"],
            None,
            ["HEAD~1..."],
            set(),
        ),
    ],
)
def test_command_line(
    repo,
    side_effect,
    dir_,
    test_path,
    src_path,
    extra_deps_file,
    git_diff_args,
    expected,
    request,
    monkeypatch,
):
    repo_path = request.getfixturevalue(repo)
    side_effect(repo_path)

    # Note paths are specified relative to repo_path since repo_path is not known beforehand
    dir_ = os.path.join(repo_path, dir_)
    test_path = [os.path.join(repo_path, p) for p in test_path]
    src_path = [os.path.join(repo_path, p) for p in src_path]

    if extra_deps_file:
        extra_deps_file = os.path.join(repo_path, extra_deps_file)

    dir_args = ["--dir", dir_]
    test_path_args = list(sum(zip(["--test-path"] * len(test_path), test_path), ()))
    src_path_args = list(sum(zip(["--src-path"] * len(src_path), src_path), ()))
    extra_deps_file_arg = (
        ["--extra-deps-file", extra_deps_file] if extra_deps_file else []
    )

    cmd = (
        ["git-select-tests"]
        + dir_args
        + test_path_args
        + src_path_args
        + extra_deps_file_arg
        + git_diff_args
    )

    with monkeypatch.context() as m:
        m.setattr(sys, "argv", cmd)
        f = io.StringIO()

        with contextlib.redirect_stdout(f):
            assert pytest_git_selector.cmd.main() == 0

        f.seek(0)

    # Expected must be in absolute paths
    expected = set(os.path.join(repo_path, p) for p in expected)

    if (output := "".join(f.readlines())).strip():
        actual = set(output.strip().split("\n"))
    else:
        actual = set()

    assert actual == expected
