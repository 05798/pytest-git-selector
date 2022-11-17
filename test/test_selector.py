import os

import git
import pytest

from pytest_git_selector.errors import UnsupportedArgumentException
from pytest_git_selector.selector import select_test_files
from conftest import (
    add_h_small_project_a,
    b_2_depends_on_a_2_medium_project_a,
    complex_workflow_a_medium_project_a,
    complex_workflow_a_medium_project_a_feature_1,
    complex_workflow_b_medium_project_a,
    complex_workflow_b_medium_project_a_feature_1,
    delete_f_small_project_a,
    modify_b_1_medium_project_a,
    modify_f_small_project_a,
    modify_f_1_txt_small_project_b,
    modify_g_small_project_a,
    modify_h_test_inputs_and_g_small_project_b,
    rename_f_small_project_a,
)


@pytest.mark.parametrize(
    (
        "repo",
        "start_dir",
        "side_effect",
        "git_diff_args",
        "test_paths",
        "python_paths",
        "dir_name",
        "extra_deps",
        "expected",
        "make_test_paths_abs",
        "make_python_paths_abs",
        "make_dir_name_abs",
    ),
    [
        (
            "small_project_a",
            ".",
            modify_f_small_project_a,
            ["HEAD~1..."],
            ["test"],
            ["."],
            ".",
            [],
            {"test/test_f.py", "test/test_g.py"},
            False,
            False,
            False,
        ),
        (
            "small_project_a",
            "..",
            modify_f_small_project_a,
            ["HEAD~1...", "--diff-filter=m"],
            ["test"],
            ["."],
            ".",
            [],
            {},
            True,
            False,
            True,
        ),
        (
            "small_project_a",
            ".",
            modify_g_small_project_a,
            ["HEAD~1..."],
            ["test"],
            ["."],
            ".",
            [],
            {"test/test_g.py"},
            False,
            True,
            False,
        ),
        (
            "small_project_a",
            ".",
            delete_f_small_project_a,
            ["HEAD~1..."],
            ["test"],
            ["."],
            ".",
            [],
            {"test/test_f.py", "test/test_g.py"},
            True,
            True,
            True,
        ),
        (
            "small_project_a",
            "..",
            rename_f_small_project_a,
            ["HEAD~1..."],
            ["test"],
            ["."],
            ".",
            [],
            {"test/test_f.py", "test/test_g.py"},
            False,
            False,
            False,
        ),
        (
            "small_project_a",
            ".",
            add_h_small_project_a,
            ["base..."],
            ["test"],
            ["."],
            ".",
            [],
            {"test/test_g.py", "test/test_h.py"},
            True,
            False,
            True,
        ),
        (
            "small_project_b",
            ".",
            modify_h_test_inputs_and_g_small_project_b,
            ["HEAD~1..."],
            ["test"],
            ["."],
            ".",
            [
                ("test/test_h.py", "test/test_h_modulo_inputs.csv"),
                ("small_project_b/f/f_1.py", "small_project_b/f/f_1.txt"),
            ],
            {"test/test_g.py", "test/test_h.py"},
            False,
            True,
            False,
        ),
        (
            "small_project_b",
            ".",
            modify_f_1_txt_small_project_b,
            ["HEAD~1..."],
            ["test"],
            ["."],
            ".",
            [
                ("test/test_h.py", "test/test_h_modulo_inputs.csv"),
                ("small_project_b/f/f_1.py", "small_project_b/f/f_1.txt"),
            ],
            {"test/test_f.py", "test/test_g.py", "test/test_h.py"},
            True,
            True,
            True,
        ),
        (
            "medium_project_a",
            ".",
            modify_b_1_medium_project_a,
            ["HEAD~1..."],
            ["test"],
            ["src"],
            ".",
            [],
            {
                "test/test_a/test_a_3.py",
                "test/test_b/test_b_1.py",
                "test/test_b/test_b.py",
                "test/test_c/test_c_1.py",
                "test/test_d/test_d_1.py",
            },
            False,
            False,
            False,
        ),
        (
            "medium_project_a",
            ".",
            b_2_depends_on_a_2_medium_project_a,
            ["HEAD~2..."],
            ["test"],
            ["src"],
            ".",
            [],
            {
                "test/test_a/test_a_2.py",
                "test/test_a/test_a_3.py",
                "test/test_b/test_b_2.py",
                "test/test_b/test_b.py",
                "test/test_c/test_c_1.py",
                "test/test_c/test_c_2.py",
                "test/test_d/test_d_1.py",
            },
            True,
            False,
            True,
        ),
        (
            "medium_project_a",
            ".",
            complex_workflow_a_medium_project_a,
            ["base..."],
            ["test"],
            ["src"],
            ".",
            [],
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
            True,
            False,
        ),
        (
            "medium_project_a",
            ".",
            complex_workflow_a_medium_project_a_feature_1,
            ["base..."],
            ["test"],
            ["src"],
            ".",
            [],
            {
                "test/test_a/test_a_1.py",
                "test/test_a/test_a_3.py",
                "test/test_b/test_b_2.py",
                "test/test_b/test_b.py",
                "test/test_c/test_c_1.py",
                "test/test_d/test_d_1.py",
            },
            True,
            True,
            True,
        ),
        (
            "medium_project_a",
            ".",
            complex_workflow_b_medium_project_a,
            ["base..."],
            ["test"],
            ["src"],
            ".",
            [],
            {
                "test/test_a/test_a_1.py",
                "test/test_a/test_a_3.py",
                "test/test_b/test_b_1.py",
                "test/test_b/test_b.py",
                "test/test_c/test_c_1.py",
                "test/test_d/test_d_1.py",
            },
            False,
            False,
            False,
        ),
        (
            "medium_project_a",
            "src/a",
            complex_workflow_b_medium_project_a_feature_1,
            ["base..."],
            ["test"],
            ["src"],
            ".",
            [],
            {
                "test/test_a/test_a_2.py",
                "test/test_a/test_a_3.py",
                "test/test_b/test_b_1.py",
                "test/test_b/test_b.py",
                "test/test_c/test_c_1.py",
                "test/test_c/test_c_2.py",
                "test/test_d/test_d_1.py",
            },
            True,
            False,
            True,
        ),
        (
            "medium_project_a",
            "test/",
            complex_workflow_b_medium_project_a_feature_1,
            ["base...", "--diff-filter=M"],
            ["test"],
            ["src"],
            ".",
            [],
            {
                "test/test_c/test_c_2.py",
                "test/test_d/test_d_1.py",
            },
            False,
            True,
            False,
        ),
        (
            "small_project_a",
            ".",
            modify_f_small_project_a,
            [],
            [],
            [],
            ".",
            [],
            set(),
            True,
            True,
            True,
        ),
        (
            "small_project_a",
            "..",
            modify_f_small_project_a,
            ["HEAD~1..."],
            [],
            [],
            ".",
            [],
            set(),
            False,
            False,
            False,
        ),
        (
            "empty_repo",
            ".",
            lambda x: None,
            ["HEAD~1..."],
            [],
            [],
            ".",
            [],
            git.InvalidGitRepositoryError,
            True,
            False,
            True,
        ),
        (
            "small_project_a",
            "..",
            rename_f_small_project_a,
            ["--diff-filter", "R", "HEAD~1..."],
            ["test"],
            ["."],
            ".",
            [],
            UnsupportedArgumentException,
            False,
            False,
            False,
        ),
        (
            "small_project_a",
            "..",
            rename_f_small_project_a,
            ["--diff-filter=R", "HEAD~1..."],
            ["test"],
            ["."],
            ".",
            [],
            UnsupportedArgumentException,
            False,
            False,
            False,
        ),
        (
            "small_project_a",
            "..",
            rename_f_small_project_a,
            ["--output", "HEAD~1..."],
            ["test"],
            ["."],
            ".",
            [],
            UnsupportedArgumentException,
            False,
            False,
            False,
        ),
    ],
)
def test_select_test_files(
    repo,
    start_dir,  # relative to repo base dir
    side_effect,
    git_diff_args,
    test_paths,  # relative to repo base dir
    python_paths,  # relative to repo base dir
    dir_name,  # relative to repo base dir
    extra_deps,
    expected,
    make_test_paths_abs,  # convert test paths to absolute paths before passing to function
    make_python_paths_abs,  # convert test paths to absolute paths before passing to function
    make_dir_name_abs,  # convert test paths to absolute paths before passing to function
    request,
):
    repo_path = request.getfixturevalue(repo)
    start_dir_abs = os.path.join(repo_path, start_dir)
    side_effect(repo_path)

    os.chdir(start_dir_abs)

    # Path handling is a little complicated since we don't know the path of the repo beforehand
    # So the tests specify all paths relative to this repo base directory and we convert to an absolute path always
    # Need to test whether the command can be run from different starting directories and difference combinations of
    # relative and absolute paths for test_paths, python_paths and dir_name args
    # If we want to test relative paths, we then convert it back relative to the STARTING directory not the repo

    test_paths = [os.path.join(repo_path, p) for p in test_paths]

    if not make_test_paths_abs:
        test_paths = [os.path.relpath(p, start_dir_abs) for p in test_paths]

    python_paths = [os.path.join(repo_path, p) for p in python_paths]

    if not make_python_paths_abs:
        python_paths = [os.path.relpath(p, start_dir_abs) for p in python_paths]

    dir_name = os.path.join(repo_path, dir_name)

    if not make_dir_name_abs:
        dir_name = os.path.relpath(dir_name, start_dir_abs)

    # Note paths are specified relative to repo_path since repo_path is not known beforehand
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            select_test_files(
                git_diff_args,
                test_paths,
                python_paths,
                dir_name=dir_name,
                extra_deps=extra_deps,
            )
    else:
        test_files = select_test_files(
            git_diff_args,
            test_paths,
            python_paths,
            dir_name=repo_path,
            extra_deps=extra_deps,
        )

        # Expected must be in absolute paths
        expected = set(os.path.join(repo_path, p) for p in expected)

        assert test_files == expected
