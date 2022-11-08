import git
import importlab.environment
import importlab.graph
import importlab.utils
import os
import networkx
import pathlib
import sys

from pytest_git_selector.util import to_absolute_path
from typing import List, MutableSet, Optional, Tuple


def select_test_files(
    git_diff_args: List[str],
    test_paths: List[str],
    python_path: List[str],
    dir_name: str = ".",
    extra_deps: Optional[List[Tuple[str, str]]] = None,
) -> MutableSet[str]:
    repo = git.Repo(dir_name)

    # Use --no-renames treats renames as a deletion of the pre-rename file and addition of the post-rename file
    # This is easier to deal with when analyzing the dependencies
    diff_files_relative_path = repo.git.diff(
        "--name-only", "--no-renames", *git_diff_args
    ).split("\n")
    # Import graph is stated in absolute paths so need absolute paths for diffs also
    diff_files = {to_absolute_path(dir_name, p) for p in diff_files_relative_path}

    import_graph = _create_import_graph(
        git_diff_args, python_path, test_paths=test_paths, dir_name=dir_name
    )

    if extra_deps:
        extra_deps = _to_absolute_path_extra_deps(extra_deps, dir_name)
        import_graph.graph.add_edges_from(extra_deps)

    root_ancestor_nodes = set()

    for node in import_graph.graph.nodes:
        filename = pathlib.Path(import_graph.format(node))

        if filename in diff_files:
            _find_root_ancestors(import_graph.graph, node, root_ancestor_nodes)

    root_ancestor_nodes = set(map(import_graph.format, root_ancestor_nodes))

    return root_ancestor_nodes


def _to_absolute_path_extra_deps(extra_deps: List[Tuple[str, str]], base_dir_name: str):
    extra_deps_absolute_paths = []

    for u, v in extra_deps:
        # Graph uses strings, not pathlib.Path so convert to strings before adding to graph
        extra_deps_absolute_paths.append(
            (
                u if os.path.isabs(u) else str(to_absolute_path(base_dir_name, u)),
                v if os.path.isabs(v) else str(to_absolute_path(base_dir_name, v)),
            )
        )

    return extra_deps_absolute_paths


def _create_import_graph(
    git_diff_args: List[str], python_path, test_paths: List[str], dir_name: str = "."
) -> importlab.graph.ImportGraph:
    repo = git.Repo(dir_name)

    deleted_files_output = repo.git.diff(
        "--name-only", "--diff-filter=D", "--no-renames", *git_diff_args
    )
    deleted_files_relative_path = (
        deleted_files_output.split("\n") if deleted_files_output else []
    )
    deleted_files = [to_absolute_path(dir_name, d) for d in deleted_files_relative_path]

    env = importlab.environment.Environment(
        importlab.environment.path_from_pythonpath(":".join(python_path)),
        sys.version_info[:2],
    )
    test_filenames = importlab.utils.expand_source_files(test_paths)

    # Restore the deleted files temporarily to resolve any import issues that may arise from deleting them
    try:
        for deleted_file in deleted_files:
            open(deleted_file, "w+").close()

        import_graph = importlab.graph.ImportGraph.create(env, test_filenames, True)
    finally:
        for deleted_file in deleted_files:
            os.remove(deleted_file)

    return import_graph


def _find_root_ancestors(
    graph: networkx.DiGraph, node: str, root_ancestors: set
) -> None:
    predecessors = list(graph.predecessors(node))

    if not predecessors:
        root_ancestors.add(node)
        return

    for predecessor in predecessors:
        _find_root_ancestors(graph, predecessor, root_ancestors)
