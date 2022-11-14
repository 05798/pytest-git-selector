import argparse
import sys

from pytest_git_selector.selector import select_test_files
from pytest_git_selector.util import parse_extra_deps_file


def parse_args():
    do_exit_and_print_usage = False

    try:
        delimiter_index = sys.argv.index("--")
        git_diff_args = sys.argv[delimiter_index + 1 :]

        if not git_diff_args:
            raise ValueError

        sys.argv[:] = sys.argv[:delimiter_index]
    except ValueError:
        git_diff_args = None
        do_exit_and_print_usage = True  # Delay raising error so that help message is populated with args below

    parser = _build_parser()

    if do_exit_and_print_usage:
        parser.print_help(sys.stderr)
        raise ValueError  # reraise the ValueError after printing help

    return parser.parse_args(), git_diff_args


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir",
        help="base directory of the project containing the .git folder. Defaults to current directory",
        default=".",
    )
    parser.add_argument(
        "--test-path",
        help=(
            "path of a test file or directory containing test files. "
            "These are relative to the current working directory not the directory specified in '--dir'. "
            "Defaults to: 'test', 'tests'"
        ),
        action="append",
        default=["test", "tests"],
    )
    parser.add_argument(
        "--src-path",
        help=(
            "path of directory containing source files for the project. "
            "These are relative to the current working directory not the directory specified in '--dir'. "
            "Defaults to: '.', 'src'"
        ),
        action="append",
        default=[".", "src"],
    )
    parser.add_argument(
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
    parser.add_argument(
        "-- ",
        metavar="[git-diff-args]",
        help=(
            "args to pass to git diff. "
            "They must be appear at the end of the args separated from the rest of the args of git-select-tests using "
            "the '--' delimiter e.g. pytest --collect-only -- --diff-filter=M HEAD~1..."
            "git diff is called internally with the --name-only and --no-renames automatically. "
            "Any additional arguments must not interfere with the output format e.g. do not use the --output flag "
            "which writes to a file instead of stdout"
        ),
    )
    return parser


def main():
    try:
        args, git_diff_args = parse_args()
    except ValueError:
        return 1

    if args.extra_deps_file:
        extra_deps = parse_extra_deps_file(args.extra_deps_file)
    else:
        extra_deps = None

    required_test_files = select_test_files(
        git_diff_args,
        args.test_path,
        args.src_path,
        dir_name=args.dir,
        extra_deps=extra_deps,
    )

    print("\n".join(required_test_files))

    return 0


if __name__ == "__main__":
    sys.exit(main())
