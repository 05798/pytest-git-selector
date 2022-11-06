import git
import os
import networkx
import sys

from importlab import environment
from importlab import graph
from importlab import utils
from typing import List, MutableSet


def select_test_files(
        git_diff_args: List[str], 
        test_paths: List[str], 
        python_path: List[str], 
        dir_name: str = "."
    ) -> MutableSet[str]:
    repo = git.Repo(dir_name)
    diff_files = repo.git.diff("--name-only", *git_diff_args).split("\n")
    py_diff_files = utils.expand_source_files(set(f for f in diff_files if f.endswith(".py")), dir_name)
    import_graph = _create_import_graph(git_diff_args, python_path, test_paths=test_paths, dir_name=dir_name)

    root_ancestor_nodes = set()

    for node in import_graph.graph.nodes:
        filename = import_graph.format(node)

        if filename in py_diff_files:
            _find_root_ancestors(import_graph.graph, node, root_ancestor_nodes)

    root_ancestor_nodes = set(map(import_graph.format, root_ancestor_nodes))

    return root_ancestor_nodes


def _create_import_graph(git_diff_args: List[str], python_path, test_paths: List[str], dir_name: str = ".") -> graph.ImportGraph:
    repo = git.Repo(dir_name)

    deleted_files_output =  repo.git.diff("--name-only", "--diff-filter=D", *git_diff_args)
    deleted_files_relative_path = deleted_files_output.split("\n") if deleted_files_output else []
    deleted_files = [os.path.join(dir_name, d) for d in deleted_files_relative_path]

    env = environment.Environment(environment.path_from_pythonpath(":".join(python_path)), sys.version_info[:2])
    test_filenames = utils.expand_source_files(test_paths)

    # Restore the deleted files temporarily to resolve any import issues that may arise from deleting them
    try:
        for deleted_file in deleted_files:
            open(deleted_file, "w+")

        import_graph = graph.ImportGraph.create(env, test_filenames, True)
    finally:
        for deleted_file in deleted_files:
            os.remove(deleted_file)
    
    return import_graph


def _find_root_ancestors(graph: networkx.DiGraph, node: str, root_ancestors: set) -> None:
    predecessors = list(graph.predecessors(node))

    if not predecessors:
        root_ancestors.add(node)
        return

    for predecessor in predecessors:
        _find_root_ancestors(graph, predecessor, root_ancestors)
