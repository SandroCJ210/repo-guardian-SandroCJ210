from collections import defaultdict, deque
import networkx as nx
from typing import Iterable
from .object_scanner import GitObject
from pathlib import Path

def parse_commit_parents(content: bytes) -> list[str]:
    lines = content.decode(errors="replace").splitlines()
    parents = [line.split()[1] for line in lines if line.startswith("parent ")]
    return parents


def build_graph(commits: Iterable[GitObject]) -> nx.DiGraph:
    graph = nx.DiGraph()
    sha_to_obj = {obj.sha: obj for obj in commits if obj.type == "commit"}

    for sha, obj in sha_to_obj.items():
        graph.add_node(sha, sha=sha, type=obj.type)
        parents = parse_commit_parents(obj.content)
        for parent_sha in parents:
            if parent_sha in sha_to_obj:
                graph.add_edge(parent_sha, sha)

    # Assign generation numbers (GN) via topological sort
    generation = {}
    for node in nx.topological_sort(graph):
        gen = max((generation.get(p, -1) for p in graph.predecessors(node)), default=-1) + 1
        generation[node] = gen
        graph.nodes[node]["generation"] = gen

    return graph

def export_graphml(graph: nx.DiGraph, out_path: Path) -> None:
    nx.write_graphml(graph, out_path)
