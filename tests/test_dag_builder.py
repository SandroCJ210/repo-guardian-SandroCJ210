from src.guardian.dag_builder import build_graph
from src.guardian.object_scanner import GitObject

def make_commit(sha: str, parents: list[str]) -> GitObject:
    """
    Helper to create a simulated Git commit object.
    """
    header_lines = []
    for p in parents:
        header_lines.append(f"parent {p}")
    content = "\n".join(header_lines + ["", "Commit message here"]).encode()
    return GitObject(type="commit", size=len(content), content=content, sha=sha)

def test_dag_generation_number():
    cA = make_commit("a1", [])
    cB = make_commit("b2", ["a1"])
    cC = make_commit("c3", ["b2"])
    cD = make_commit("d4", ["a1", "c3"])  

    graph = build_graph([cA, cB, cC, cD])

    assert graph.nodes["a1"]["generation"] == 0
    assert graph.nodes["b2"]["generation"] == 1
    assert graph.nodes["c3"]["generation"] == 2
    assert graph.nodes["d4"]["generation"] == 3


    assert set(graph.predecessors("b2")) == {"a1"}
    assert set(graph.predecessors("c3")) == {"b2"}
    assert set(graph.predecessors("d4")) == {"a1", "c3"}
