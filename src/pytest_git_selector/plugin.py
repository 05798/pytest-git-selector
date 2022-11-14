from typing import List

import pytest

from pytest_git_selector.selector import select_test_files
from pytest_git_selector.util import parse_extra_deps_file


git_diff_args_key = pytest.StashKey[List[str]]()


def pytest_load_initial_conftests(early_config, parser, args):
    # Need to split on "--" delimiter to separate args to pytest versus args to git diff

    try:
        delimiter_index = args.index("--")
    except ValueError:
        return

    early_config.stash[git_diff_args_key] = args[delimiter_index + 1 :]
    args[:] = args[:delimiter_index]


def pytest_addoption(parser):
    group = parser.getgroup("pytest-git-selector")
    group.addoption(
        "--src-path",
        action="append",
        help=(
            "args to pass to git diff. "
            "git diff is called internally with the --name-only and --no-renames automatically. "
            "Any additional arguments must not interfere with the output format e.g. do not use the --output flag "
            "which writes to a file instead of stdout"
        ),
        default=[".", "./src/"],
    )
    group.addoption(
        "--extra-deps-file",
        help=(
            "path of a file specifying extra module dependencies not captured by Python import statements. "
            "Edges should be in the form '(a.py,b.json)' where a.py depends on b.json. "
            "Edges separated by a space or newline. "
            "NOTE there is NO space after the comma. "
            "If edges are specified using relative paths, they interpreted as being relative to the directory "
            "containing the project root directory containing the .git folder."
        ),
        default=None,
    )
    # Add a dummy option to document the -- delimiter
    group.addoption(
        "-- ",
        metavar="[git-diff-args]",
        help=(
            "args to pass to git diff. "
            "They must be appear at the end of the args separated from the rest of the args of pytest using the "
            "'--' delimiter e.g. pytest --collect-only -- --diff-filter=M HEAD~1..."
            "git diff is called internally with the --name-only and --no-renames automatically. "
            "Any additional arguments must not interfere with the output format e.g. do not use the --output flag "
            "which writes to a file instead of stdout"
        ),
    )


@pytest.hookimpl()
def pytest_collection_modifyitems(session, config, items):
    all_test_files = list(set(str(item.path) for item in items))  # remove duplicates

    if git_diff_args := config.stash.get(git_diff_args_key, None):
        if extra_deps_filename := config.getoption("--extra-deps-file"):
            extra_deps = parse_extra_deps_file(extra_deps_filename)
        else:
            extra_deps = None

        selected_items = select_test_files(
            git_diff_args,
            all_test_files,
            config.getoption("--src-path"),
            str(session.startpath),
            extra_deps=extra_deps,
        )

        deselected = [
            item for item in session.items if str(item.path) not in selected_items
        ]
        config.hook.pytest_deselected(items=deselected)

        # Docs say this should be done in-place
        items[:] = [item for item in session.items if str(item.path) in selected_items]
