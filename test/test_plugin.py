import os
import pytest

from conftest import (
    complex_workflow_a_medium_project_a,
    modify_f_small_project_a,
    modify_g_small_project_a,
    modify_h_test_inputs_and_g_small_project_b,
)


@pytest.mark.parametrize(
    (
        "repo",
        "side_effect",
        "src_path",
        "extra_deps_file",
        "git_diff_args",
        "expected_outcomes",
    ),
    [
        (
            "small_project_a",
            modify_f_small_project_a,
            ["."],
            None,
            ["HEAD~1"],
            {"passed": 2},
        ),
        (
            "small_project_a",
            modify_g_small_project_a,
            ["."],
            None,
            ["HEAD~1"],
            {"passed": 1, "deselected": 1},
        ),
        (
            "small_project_a",
            modify_f_small_project_a,
            ["."],
            None,
            ["HEAD~1...", "--diff-filter=m"],
            {"passed": 0, "deselected": 2},
        ),
        (
            "small_project_b",
            modify_h_test_inputs_and_g_small_project_b,
            ["."],
            "extra_deps.txt",
            ["HEAD~1..."],
            {"passed": 3, "deselected": 3},
        ),
        (
            "medium_project_a",
            complex_workflow_a_medium_project_a,
            ["."],
            None,
            ["base..."],
            {
                "deselected": 1,
                "errors": 2,
            },  # errors since the workflow deletes a source file without changing imports
        ),
    ],
)
def test_plugin(
    repo,
    side_effect,
    src_path,
    extra_deps_file,
    git_diff_args,
    expected_outcomes,
    pytester,
    request,
):
    repo_path = request.getfixturevalue(repo)
    os.chdir(repo_path)
    side_effect(repo_path)

    pytester.syspathinsert(repo_path)
    pytester.syspathinsert(os.path.join(repo_path, "src/"))

    src_path = [os.path.join(repo_path, p) for p in src_path]
    src_path_args = list(sum(zip(["--src-path"] * len(src_path), src_path), ()))

    if extra_deps_file:
        extra_deps_file = os.path.join(repo_path, extra_deps_file)
        extra_deps_file_args = ["--extra-deps-file", extra_deps_file]
    else:
        extra_deps_file_args = []

    git_diff_args_w_flag = ["--git-diff-args"] + git_diff_args

    result = pytester.runpytest(
        f"--basetemp={pytester.path.parent.joinpath('basetemp')}",
        *(src_path_args + extra_deps_file_args + git_diff_args_w_flag),
    )

    result.assert_outcomes(**expected_outcomes)
