from src.guardian.dag_builder import build_graph
from src.guardian.object_scanner import GitObject
import networkx as nx

def test_dag_generation_number():
    c1 = GitObject("commit", 0, b"", "a1")
    c2 = GitObject("commit", 0, b"", "b2")
    c3 = GitObject("commit", 0, b"", "c3")

    c2.parents = ["a1"]
    c3.parents = ["b2"]

    graph = build_graph([c1, c2, c3])
    assert graph.nodes["a1"]["generation"] == 0
    assert graph.nodes["b2"]["generation"] == 1
    assert graph.nodes["c3"]["generation"] == 2
