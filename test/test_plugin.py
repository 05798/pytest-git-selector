import os
import pytest

from conftest import (
    complex_workflow_a_medium_project_a,
    modify_f_small_project_a,
    modify_g_small_project_a,
)


@pytest.mark.parametrize(
    ("repo", "side_effect", "git_diff_args", "src_path", "expected_outcomes"),
    [
        ("small_project_a", modify_f_small_project_a, ["HEAD~1"], ["."], {"passed": 2}),
        (
            "small_project_a",
            modify_g_small_project_a,
            ["HEAD~1"],
            ["."], 
            {"passed": 1, "deselected": 1},
        ),
        (
            "medium_project_a",
            complex_workflow_a_medium_project_a,
            ["base..."],
            ["src"], 
            {
                "deselected": 1,
                "errors": 2,
            },  # errors since the workflow deletes a source file without changing imports
        ),
    ],
)
def test_plugin(repo, side_effect, git_diff_args, src_path, expected_outcomes, pytester, request):
    repo_path = request.getfixturevalue(repo)
    os.chdir(repo_path)
    side_effect(repo_path)

    pytester.syspathinsert(repo_path)
    pytester.syspathinsert(os.path.join(repo_path, "src/"))

    src_path = [os.path.join(repo_path, p) for p in src_path]
    src_path_args = sum(zip(["--src-path"] * len(src_path), src_path), ())

    result = pytester.runpytest(*(list(src_path_args) + ["--git-diff-args"] + git_diff_args))

    result.assert_outcomes(**expected_outcomes)
