import git
import os
import pytest

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
    ("repo", "side_effect", "git_diff_args", "test_paths", "python_paths", "extra_deps", "expected"),
    [
        (
            "small_project_a",
            modify_f_small_project_a,
            ["HEAD~1..."],
            ["test"],
            ["."],
            [],
            {"test/test_f.py", "test/test_g.py"},
        ),
        (
            "small_project_a",
            modify_f_small_project_a,
            ["HEAD~1...", "--diff-filter=m"],
            ["test"],
            ["."],
            [],
            {},
        ),
        (
            "small_project_a",
            modify_g_small_project_a,
            ["HEAD~1..."],
            ["test"],
            ["."],
            [],
            {"test/test_g.py"},
        ),
        (
            "small_project_a",
            delete_f_small_project_a,
            ["HEAD~1..."],
            ["test"],
            ["."],
            [],
            {"test/test_f.py", "test/test_g.py"},
        ),
        (
            "small_project_a",
            rename_f_small_project_a,
            ["HEAD~1..."],
            ["test"],
            ["."],
            [],
            {"test/test_f.py", "test/test_g.py"},
        ),
        (
            "small_project_a",
            add_h_small_project_a,
            ["base..."],
            ["test"],
            ["."],
            [],
            {"test/test_g.py", "test/test_h.py"},
        ),
        (
            "small_project_b",
            modify_h_test_inputs_and_g_small_project_b,
            ["HEAD~1..."],
            ["test"],
            ["."],
            [
                ("test/test_h.py", "test/test_h_modulo_inputs.csv"), 
                ("small_project_b/f/f_1.py", "small_project_b/f/f_1.txt")
            ],
            {"test/test_g.py", "test/test_h.py"},
        ),
        (
            "small_project_b",
            modify_f_1_txt_small_project_b,
            ["HEAD~1..."],
            ["test"],
            ["."],
            [
                ("test/test_h.py", "test/test_h_modulo_inputs.csv"), 
                ("small_project_b/f/f_1.py", "small_project_b/f/f_1.txt")
            ],
            {"test/test_f.py", "test/test_g.py", "test/test_h.py"},
        ),
        (
            "medium_project_a",
            modify_b_1_medium_project_a,
            ["HEAD~1..."],
            ["test"],
            ["src"],
            [],
            {
                "test/test_a/test_a_3.py",
                "test/test_b/test_b_1.py",
                "test/test_b/test_b.py",
                "test/test_c/test_c_1.py",
                "test/test_d/test_d_1.py",
            },
        ),
        (
            "medium_project_a",
            b_2_depends_on_a_2_medium_project_a,
            ["HEAD~2..."],
            ["test"],
            ["src"],
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
        ),
        (
            "medium_project_a",
            complex_workflow_a_medium_project_a,
            ["base..."],
            ["test"],
            ["src"],
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
        ),
        (
            "medium_project_a",
            complex_workflow_a_medium_project_a_feature_1,
            ["base..."],
            ["test"],
            ["src"],
            [],
            {
                "test/test_a/test_a_1.py",
                "test/test_a/test_a_3.py",
                "test/test_b/test_b_2.py",
                "test/test_b/test_b.py",
                "test/test_c/test_c_1.py",
                "test/test_d/test_d_1.py",
            },
        ),
        (
            "medium_project_a",
            complex_workflow_b_medium_project_a,
            ["base..."],
            ["test"],
            ["src"],
            [],
            {
                "test/test_a/test_a_1.py",
                "test/test_a/test_a_3.py",
                "test/test_b/test_b_1.py",
                "test/test_b/test_b.py",
                "test/test_c/test_c_1.py",
                "test/test_d/test_d_1.py",
            },
        ),
        (
            "medium_project_a",
            complex_workflow_b_medium_project_a_feature_1,
            ["base..."],
            ["test"],
            ["src"],
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
        ),
        (
            "medium_project_a",
            complex_workflow_b_medium_project_a_feature_1,
            ["base...", "--diff-filter=M"],
            ["test"],
            ["src"],
            [],
            {
                "test/test_c/test_c_2.py",
                "test/test_d/test_d_1.py",
            },
        ),
        (
            "small_project_a",
            modify_f_small_project_a,
            [],
            [],
            [],
            [],
            set(),
        ),
        (
            "small_project_a",
            modify_f_small_project_a,
            ["HEAD~1..."],
            [],
            [],
            [],
            set(),
        ),
        (
            "empty_repo",
            lambda x: None,
            ["HEAD~1..."],
            [],
            [],
            [],
            git.InvalidGitRepositoryError,
        ),
    ],
)
def test_select_test_files(
    repo, side_effect, git_diff_args, test_paths, python_paths, extra_deps, expected, request
):
    repo_path = request.getfixturevalue(repo)
    side_effect(repo_path)

    test_paths = [os.path.join(repo_path, p) for p in test_paths]
    python_paths = [os.path.join(repo_path, p) for p in python_paths]

    # Note paths are specified relative to repo_path since repo_path is not known beforehand
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            select_test_files(
                git_diff_args,
                test_paths,
                python_paths,
                dir_name=repo_path,
                extra_deps=extra_deps
            )
    else:
        test_files = select_test_files(
            git_diff_args,
            test_paths,
            python_paths,
            dir_name=repo_path,
            extra_deps=extra_deps
        )

        # Expected must be in absolute paths
        expected = set(os.path.join(repo_path, p) for p in expected)

        assert test_files == expected
