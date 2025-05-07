from src.guardian.jw_detector import is_rewrite

def test_detect_rewrite_similar_chains():
    path_a = ["a1", "b2", "c3", "d4"]
    path_b = ["x1", "b2", "c3", "d4"] 
    assert is_rewrite(path_a, path_b) is True

def test_detect_rewrite_different_chains():
    path_a = ["a1", "b2", "c3"]
    path_b = ["x9", "y8", "z7"]
    assert is_rewrite(path_a, path_b) is False

def test_detect_rewrite_edge_cases():
    assert is_rewrite([], []) is False
    assert is_rewrite(["a1"], []) is False
