import pathlib
import os
from typing import List, Tuple


def parse_extra_deps_file(extra_deps_filename) -> List[Tuple[str, str]]:
    with open(extra_deps_filename, "r") as f:
        edges = []
        for line in f:
            # Edges should be whitespace separated in the form (a,b)
            edges.extend(tuple(e.strip("()").split(",")) for e in line.split())

    return edges


def to_absolute_path(base_dir_name: str, relative_path: str) -> pathlib.Path:
    if not os.path.isabs(base_dir_name):
        base_dir_name = os.path.join(os.getcwd(), base_dir_name)
    return pathlib.Path(os.path.join(base_dir_name, relative_path)).resolve()
