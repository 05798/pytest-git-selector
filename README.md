# pytest-git-selector

## Introduction

`pytest-git-selector` is a simple project to automatically select tests that have been affected by code changes. This is mainly useful for reducing the number of tests in frequently run CI/CD jobs on feature branches (e.g. running tests based on differences between the merge base and the feature branch).

## Idea

The idea is fairly simple:

1. Changes are analyzed using a `git diff` command. The arguments to `git diff` are supplied by the user
2. If a test module contains one of the changed files in its import tree, then select that test module

The import tree is created using [`importlab`](https://github.com/google/importlab) which statically analyzes import statements to determine dependencies.

See the [git-diff documentation](https://git-scm.com/docs/git-diff) for arguments that can be supplied to `git diff`.

## `pytest` plugin

The plugin will automatically deselect tests whose descendants in the dependency tree have not changed. The changed are determined via a `git diff` command that is called with user supplied argument. User supplied arguments to `git diff` must be appear at the end of the `pytest` arguments separated from the rest of the `pytest` arguments using the `--` delimiter e.g. 

```
pytest --collect-only -- --diff-filter=M HEAD~1...
```

This plugin adds two additional flags to `pytest`: 

1. `--src-path` - specifies the directory containing the source code for the project. `src` and the current working directory are automatically added so this argument should not be required in most cases
2. `--extra-deps-file` - specifies a path to a file containing dependencies between files not captured by Python import statements e.g. test input files. Edges should be in the form '(a.py,b.json)' where a.py depends on b.json. Edges separated by a space or newline. NOTE there is NO space after the comma. If edges are specified using relative paths, they interpreted as being relative to the directory containing the project root directory containing the .git folder.

### Examples

The following examples assume the project contains source code in `<project_root>/src/` and tests in `<project_root>/test/`. `pytest` is run in `<project_root>` in all the following examples.

#### Selecting tests affected by changes between a feature branch and its merge base
```
pytest -- main...
```

#### Selecting tests affected by changes in the last commit
```
pytest -- HEAD~1...
```

#### Selecting tests affected by changes between two commits with an extra dependency file `extra_deps.txt` specified and source code in `custom_src_dir/`
```
pytest --src-path custom_src_dir/ --extra-deps-file extra_deps.txt -- 1b23b4b1...12da93k8
```
## Command line tool

The `git-select-tests` command line tool can be used to print out selected test modules. This is mainly useful for projects that do not use `pytest` as a test runner e.g. `nosetest`. The arguments to the `git diff` command are separated by the `--` delimiter. See `git-select-tests --help` for usage.

### Examples

The following examples assume the project contains source code in `<project_root>/src/` and tests in `<project_root>/test/`.

#### Selecting tests affected by changes between a feature branch and its merge base

```
git-select-tests --src-path src/ --test-path test/ -- main...
```

#### Selecting tests affected by changes in the last commit
```
git-select-tests --src-path src/ --test-path test/ -- HEAD~1...
```

## Comparison with `pytest-diff-selector`

This idea has been implemented before in this `pytest-diff-selector` [project](https://github.com/fruch/pytest-diff-selector). The main differences are:
1. `pytest-git-selector` leverages the `importlab` library as opposed to using a proprietary static analyzer
2. `pytest-git-selector` implements a `pytest` plugin

Currently `pytest-diff-selector` does not appear to be working and has not been updated recently which is the reason for this project's existence. 
