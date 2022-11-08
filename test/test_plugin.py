import os
import pytest

from conftest import (
    complex_workflow_a_medium_project_a,
    modify_f_small_project_a,
    modify_g_small_project_a,
)


@pytest.mark.parametrize(
    ("repo", "side_effect", "git_diff_args", "expected_outcomes"),
    [
        ("small_project_a", modify_f_small_project_a, ["HEAD~1"], {"passed": 2}),
        (
            "small_project_a",
            modify_g_small_project_a,
            ["HEAD~1"],
            {"passed": 1, "deselected": 1},
        ),
        (
            "medium_project_a",
            complex_workflow_a_medium_project_a,
            ["base..."],
            {
                "deselected": 1,
                "errors": 2,
            },  # errors since the workflow deletes a source file without changing imports
        ),
    ],
)
def test_plugin(repo, side_effect, git_diff_args, expected_outcomes, pytester, request):
    repo_path = request.getfixturevalue(repo)
    os.chdir(repo_path)
    side_effect(repo_path)

    pytester.syspathinsert(repo_path)
    pytester.syspathinsert(os.path.join(repo_path, "src/"))

    result = pytester.runpytest("--git-diff-args", *git_diff_args)

    result.assert_outcomes(**expected_outcomes)
