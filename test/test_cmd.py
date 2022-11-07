import logging
import os
import pytest
import subprocess

from conftest import (
    complex_workflow_a_medium_project_a,
    modify_f_small_project_a,
)

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger()


# To run these tests, you will need to install the package in editable mode so that subprocess can use the entry point
@pytest.mark.parametrize(
    ("repo", "side_effect", "dir_", "test_path", "src_path", "subargs", "expected"),
    [
        (
            "small_project_a",
            modify_f_small_project_a,
            ".",
            ["test"],
            ["."],
            ["HEAD~1..."],
            {"test/test_f.py", "test/test_g.py"},
        ),
        (
            "medium_project_a",
            complex_workflow_a_medium_project_a,
            ".",
            ["test"],
            ["src"],
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
            ["HEAD~1..."],
            set(),
        ),
    ],
)
def test_command_line(
    repo, side_effect, dir_, test_path, src_path, subargs, expected, request
):
    repo_path = request.getfixturevalue(repo)
    side_effect(repo_path)

    # Note paths are specified relative to repo_path since repo_path is not known beforehand
    dir_ = os.path.join(repo_path, dir_)
    test_path = [os.path.join(repo_path, p) for p in test_path]
    src_path = [os.path.join(repo_path, p) for p in src_path]

    test_path_args = sum(zip(["--test-path"] * len(test_path), test_path), ())
    src_path_args = sum(zip(["--src-path"] * len(src_path), src_path), ())

    try:
        output = subprocess.check_output(
            ["git-select-tests", "--dir", dir_]
            + list(test_path_args)
            + list(src_path_args)
            + subargs
        )
    except subprocess.CalledProcessError as cpe:
        _logger.error(f"Exit code {cpe.returncode} : {cpe.output}")
        assert False

    # Expected must be in absolute paths
    expected = set(os.path.join(repo_path, p) for p in expected)
    actual = set(output.decode().strip().split("\n")) if output.strip() else set()

    assert actual == expected
