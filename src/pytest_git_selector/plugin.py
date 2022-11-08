import pytest
import pytest_git_selector.selector


def pytest_addoption(parser):
    group = parser.getgroup("pytest-git-selector")
    group.addoption("--git-diff-args", nargs="*", help="args to pass to git diff")
    group.addoption(
        "--src-path",
        action="append",
        help="args to pass to git diff",
        default=[".", "./src/"],
    )


@pytest.hookimpl()
def pytest_collection_modifyitems(session, config, items):
    all_test_files = list(set(str(item.path) for item in items))  # remove duplicates
    git_diff_args = config.getoption("--git-diff-args")

    if git_diff_args:
        selected_items = pytest_git_selector.selector.select_test_files(
            git_diff_args,
            all_test_files,
            config.getoption("--src-path"),
            str(session.startpath),
        )

        deselected = [
            item for item in session.items if str(item.path) not in selected_items
        ]
        config.hook.pytest_deselected(items=deselected)

        # Docs say this should be done in-place
        items[:] = [item for item in session.items if str(item.path) in selected_items]
