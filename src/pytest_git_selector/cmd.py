import argparse
import pytest_git_selector.selector


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dir",
        help="base directory of the project containing the .git folder",
        default=".",
    )
    parser.add_argument(
        "--test-path",
        help="path of a test file or directory containing test files. These are relative to the current working directory not the directory specified in '--dir'",
        required=True,
        action="append"
    )
    parser.add_argument(
        "--src-path",
        help="path of directory containing source files for the project. These are relative to the current working directory not the directory specified in '--dir'",
        required=True,
        action="append"
    )
    parser.add_argument(
        "subargs",
        nargs=argparse.REMAINDER,
        help='Arguments to pass to git diff command. Note that "--name-only" will automatically be included',
    )
    return parser.parse_args()


def main():
    args = parse_args()

    required_test_files = pytest_git_selector.selector.select_test_files(
        args.subargs, args.test_path, args.src_path, dir_name=args.dir
    )

    print("\n".join(required_test_files))

    return 0


if __name__ == "__main__":
    exit(main())
