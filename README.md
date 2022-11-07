# pytest-git-selector

## Introduction

`pytest-git-selector` is a simple project to automatically select tests that have been affected by code changes. This is mainly useful for reducing the number of tests in frequently run CI/CD jobs on feature branches (e.g. push, opening a pull request).


## Idea

The idea is fairly simple:

1. Changes are analyzed using a `git diff` command. The arguments `git diff` are supplied by the user
2. If a test module contains one of the changed files in its import tree, then select that test module

The import tree is created using [`importlab`](https://github.com/google/importlab) which statically analyzes import statements to determine dependencies.

## Quickstart

The `git-select-tests` command line tool can be used to print out selected test modules. `--src-path` for the git repository
under analysis must be provided to ensure `importlab` can resolve the import statements to a source file. `--test-path` must be provided currently for the purposes of test discovery. Arguments not specified via a flag are passed to `git diff`. 

See `git-select-tests --help` for usage.

See the [git-diff documentation](https://git-scm.com/docs/git-diff) for arguments that can be supplied to `git diff`.

### Examples

The following examples assume the project contains source code in `<project_root>/src/` and tests in `<project_root>/test/`.

#### Selecting tests affected by changes between a feature branch and its merge base

```
git-select-tests --src-path src/ --test-path test/ main...
```

#### Selecting tests affected by changes in the last commit
```
git-select-tests --src-path src/ --test-path test/ HEAD~1...
```

## Comparison with `pytest-diff-selector`

This idea has been implemented before in this [`pytest-diff-selector` project](https://github.com/fruch/pytest-diff-selector). The main differences is`pytest-git-selector` leverages the `importlab` library as opposed to using a proprietary static analyzer.

Currently `pytest-diff-selector` does not appear to be working and has not been updated recently which is the reason for this project's existence.
