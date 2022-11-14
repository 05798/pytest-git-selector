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
        "start_dir",
        "side_effect",
        "dir_",
        "test_path",
        "src_path",
        "extra_deps_file",
        "git_diff_args",
        "expected",
        "make_dir_abs",
        "make_test_path_abs",
        "make_src_path_abs",
        "make_extra_deps_file_abs",
    ),
    [
        (
            "small_project_a",
            "..",
            modify_f_small_project_a,
            ".",
            ["test"],
            ["."],
            None,
            ["HEAD~1..."],
            {"test/test_f.py", "test/test_g.py"},
            True,
            True,
            False,
            False,
        ),
        (
            "small_project_a",
            ".",
            modify_f_small_project_a,
            ".",
            ["test"],
            ["."],
            None,
            ["HEAD~1...", "--diff-filter=m"],
            set(),
            False,
            False,
            True,
            False,
        ),
        (
            "small_project_b",
            "small_project_b/f",
            modify_f_1_txt_small_project_b,
            ".",
            ["test"],
            ["."],
            "extra_deps.txt",
            ["HEAD~1..."],
            {"test/test_f.py", "test/test_g.py", "test/test_h.py"},
            False,
            True,
            False,
            False,
        ),
        (
            "medium_project_a",
            ".",
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
            False,
            False,
            False,
            False,
        ),
        (
            "small_project_a",
            "..",
            modify_f_small_project_a,
            ".",
            ["fake"],
            ["fake"],
            None,
            ["HEAD~1..."],
            set(),
            False,
            False,
            False,
            False,
        ),
        (
            "small_project_a",
            "..",
            modify_f_small_project_a,
            ".",
            ["fake"],
            ["fake"],
            None,
            [],
            1,
            False,
            False,
            False,
            False,
        ),
    ],
)
def test_command_line(
    repo,
    start_dir,
    side_effect,
    dir_,
    test_path,
    src_path,
    extra_deps_file,
    git_diff_args,
    expected,
    make_dir_abs,
    make_test_path_abs,
    make_src_path_abs,
    make_extra_deps_file_abs,
    request,
    monkeypatch,
):
    repo_path = request.getfixturevalue(repo)
    start_dir_abs = os.path.join(repo_path, start_dir)
    side_effect(repo_path)

    os.chdir(start_dir_abs)

    cmd = _build_command(
        repo_path,
        start_dir_abs,
        dir_,
        test_path,
        src_path,
        extra_deps_file,
        git_diff_args,
        make_dir_abs,
        make_test_path_abs,
        make_src_path_abs,
        make_extra_deps_file_abs,
    )

    expected_exit_code = expected if isinstance(expected, int) else 0

    with monkeypatch.context() as m:
        m.setattr(sys, "argv", cmd)
        f = io.StringIO()

        with contextlib.redirect_stdout(f):
            assert pytest_git_selector.cmd.main() == expected_exit_code

        if expected_exit_code != 0:
            return

        f.seek(0)

    # Expected must be in absolute paths
    expected = set(os.path.join(repo_path, p) for p in expected)

    if (output := "".join(f.readlines())).strip():
        actual = set(output.strip().split("\n"))
    else:
        actual = set()

    assert actual == expected


def _build_command(
    repo_path,
    start_dir_abs,
    dir_,
    test_path,
    src_path,
    extra_deps_file,
    git_diff_args,
    make_dir_abs,
    make_test_path_abs,
    make_src_path_abs,
    make_extra_deps_file_abs,
):
    # Note paths are specified relative to repo_path since repo_path is not known beforehand
    dir_ = os.path.join(repo_path, dir_)

    if not make_dir_abs:
        dir_ = os.path.relpath(dir_, start_dir_abs)

    test_path = [os.path.join(repo_path, p) for p in test_path]

    if not make_test_path_abs:
        test_path = [os.path.relpath(p, start_dir_abs) for p in test_path]

    src_path = [os.path.join(repo_path, p) for p in src_path]

    if not make_src_path_abs:
        src_path = [os.path.relpath(p, start_dir_abs) for p in src_path]

    if extra_deps_file:
        extra_deps_file = os.path.join(repo_path, extra_deps_file)

        if not make_extra_deps_file_abs:
            extra_deps_file = os.path.relpath(extra_deps_file, start_dir_abs)

    dir_args = ["--dir", dir_]
    test_path_args = list(sum(zip(["--test-path"] * len(test_path), test_path), ()))
    src_path_args = list(sum(zip(["--src-path"] * len(src_path), src_path), ()))
    extra_deps_file_arg = (
        ["--extra-deps-file", extra_deps_file] if extra_deps_file else []
    )
    git_diff_args_w_delimiter = ["--"] + git_diff_args

    return (
        ["git-select-tests"]
        + dir_args
        + test_path_args
        + src_path_args
        + extra_deps_file_arg
        + git_diff_args_w_delimiter
    )
