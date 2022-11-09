import argparse

from pytest_git_selector.selector import select_test_files
from pytest_git_selector.util import parse_extra_deps_file


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir",
        help="base directory of the project containing the .git folder",
        default=".",
    )
    parser.add_argument(
        "--test-path",
        help=(
            "path of a test file or directory containing test files. "
            "These are relative to the current working directory not the directory specified in '--dir'"
        ),
        required=True,
        action="append",
    )
    parser.add_argument(
        "--src-path",
        help=(
            "path of directory containing source files for the project. "
            "These are relative to the current working directory not the directory specified in '--dir'"
        ),
        required=True,
        action="append",
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
    parser.add_argument(
        "git-diff-args",
        nargs=argparse.REMAINDER,
        help=(
            "args to pass to git diff. "
            "git diff is called internally with the --name-only and --no-renames automatically. "
            "Any additional arguments must not interfere with the output format e.g. do not use the --output flag "
            "which writes to a file instead of stdout"
        ),
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.extra_deps_file:
        extra_deps = parse_extra_deps_file(args.extra_deps_file)
    else:
        extra_deps = None

    required_test_files = select_test_files(
        vars(args)["git-diff-args"],
        args.test_path,
        args.src_path,
        dir_name=args.dir,
        extra_deps=extra_deps,
    )

    print("\n".join(required_test_files))

    return 0


if __name__ == "__main__":
    exit(main())
