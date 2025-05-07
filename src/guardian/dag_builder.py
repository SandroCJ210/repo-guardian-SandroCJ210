from collections import defaultdict, deque
import networkx as nx
from typing import Iterable
from .object_scanner import GitObject

def build_graph(commits: Iterable[GitObject]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for commit in commits:
        graph.add_node(commit.sha, type=commit.type)

        parents = getattr(commit, "parents", [])
        for parent in parents:
            graph.add_edge(parent, commit.sha)

    gn = {}
    for node in nx.topological_sort(graph):
        gn[node] = max([gn.get(p, -1) for p in graph.predecessors(node)] + [-1]) + 1
        graph.nodes[node]["generation"] = gn[node]

    return graph
